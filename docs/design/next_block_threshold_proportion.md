# Thresholds in proportion to the physics: a proposal for the next block's registration

Design note, 2026-10-12, written by the orchestrator (Opus 5.5) for the owner's ask of 2026-10-10:
"proportion of physics boundaries, check to make sure we're not arbitrarily being too strict with something
that doesnt make sense".

**This note proposes. It changes no sealed text, no code and no block-5 number.** Block 5's registration,
analysis plan and harvest stay exactly as sealed, and its analysis stays blinded: no block-5 energy, power or
duration was opened to write this, and none appears below. Every size used here comes from a non-claim
rehearsal on a quiet machine (2026-10-09), from the calibration acceptance derived before block 5, or from
design text. The sizes are therefore good enough to judge proportion and are not results. The proposals are
for the registration of the block after block 5, and section 5 says which of them need a review before that
registration can be sealed.

Inputs: the read-only audit `thresholds-audit.md`, `why-125-runs.md`, `network-time-options.md` and the
power-trace notes under `/Users/edr/night-archive/b5-consults/ed-1010-asks/` (outside the repository), items
14, 17, 19, 22 and 29 of the top block of `RUN_STATE.md`, and a comparison with three published power
benchmarks (section 6).

## 0. Words used

Five words name five different things. Older text, code identifiers and the sealed registration call most of
them "window"; this note does not.

- **Session**: one unattended collection of several hours on one machine state. It holds an opening
  calibration, about 125 runs and a closing calibration.
- **Attempt**: one try at a session. A session that fails is attempted again.
- **Run**: one execution of one model on one fixed prompt, with the processor's power recorded around it
  (the code says "member").
- **Measured interval**: inside a run, the span from the start marker to the end marker of the request. About
  3 s of a run's roughly 237 s; the rest is setup, idle sampling and cool-down.
- **Phase interval**: one of the two parts of the measured interval. **Prefill** is the model reading the
  prompt and producing the first token. **Decode** is the model producing the remaining tokens. The reported
  quantity is the energy of one phase interval, in joules.

Other terms, each built here because the table depends on it:

- **Record**: one line of output from the power sampler (the macOS tool `powermetrics`). It is the *average*
  processor power over about 130.5 ms, labelled with a calendar time rounded to a whole second.
- **Timing bound**: the largest amount, in milliseconds, by which the records could be misplaced in time
  against the phase boundaries. Records are stamped by the sampler; phase boundaries are stamped by the
  workload; the two have to be laid on one timeline, and the timing bound is how wrong that laying-on can be.
- **Alignment capture**: a calibration taken at the start and at the end of a session. The machine produces
  power pulses at known times, and the capture measures how far the sampler's records sit from those known
  times. Its output is one number in milliseconds, the capture's timing bound.
- **Operative timing bound** (`b_op`): the timing bound used for a whole session:
  `b_op = max(opening, closing) + max(|closing - opening|, 14.531 ms)`. The first term is the worse of the two
  captures; the second pays for the alignment moving between them, with 14.531 ms as a fixed minimum.
- **Attribution floor**: how many joules a phase energy can move when the records slide by the timing bound.
  It is printed beside every reported number. It is the largest uncertainty the project states.
- **Reference**: a run of one fixed small workload, placed at the start, middle and end of a session.
  **Corpus**: 18 runs of that same workload at the very start. **Drift screen**: the comparison of the end
  references with the start references; the session is removed when they differ by more than a bound
  computed from the scatter of the corpus (the code calls this screen NEG-8).
- **Quad**: four runs in the order A, B, B, A, so that a steady drift adds equally to A and to B and cancels
  in A minus B. **Unit**: one independent draw for the statistics; a quad counts as one unit, and a run taken
  alone (an "absolute repeat") counts as one unit. **Stratum**: one group of like units (the repeats of one
  phase, or the quads of one phase).
- **Idle baseline**: 576 records (75 s) of processor power taken before a run, with nothing running.
  **Idle admission**: the rule that decides from the idle baseline whether the run may start. **p95**: the
  value that 95% of the records lie under.
- **Contention**: another process using the processor while a run is measured, so that its energy is counted
  as the model's. It is measured in CPU-seconds per second: 0.05 means the process kept 5% of one core busy.
- **Refusal** and **flag**: a refusal stops or removes data. A flag is a recorded fact written beside the
  data; the analysis plan, fixed in advance, says which flags exclude a run or a session from a claim.
- **Seal**: freezing a block's registration, plan and code before collection. **Erratum**: a recorded change
  to sealed text that applies only from then on. **Council**: two reviewers of different model families
  answering one question without seeing each other's answer. **Cold gate**: a judge with no prior context
  who admits or refuses a sealed object.

## 1. The rule

Every numeric boundary in the next registration is written three ways: its value in its own unit, the error
in joules that the reported phase energy would carry if the guarded quantity sat exactly at the boundary, and
that error as a percentage of the phase energy it guards. A boundary whose error is smaller than the
attribution floor does not remove data. It becomes a flag, and where the quantity is a timing bound its actual
value is simply carried into the printed floor. A boundary keeps the power to refuse only when it names a
physical hazard that makes the printed uncertainty itself untrue (a clock jump inside a run, a sleeping
machine, a sampler that is not sampling, a second workload of several watts) or when it marks the point
where the estimator stops being defined. A boundary that is a statistic of a small sample (for example "the
largest of 24 good captures") is never used as a pass line, because a line drawn at the largest of 24 is
crossed by 1 good capture in 25 by construction.

### The sizes the rule is applied with

All from the quiet-machine rehearsal of 2026-10-09 (53 runs) unless marked.

| Quantity | Size |
|---|---|
| Prefill phase, 1.7B model, 2,048-token prompt | 26.1 J over 0.62 s, so 26.1 / 0.62 = 42 W; 6 to 7 records |
| Decode phase, 1.7B model, 512 tokens | 51.3 J over 1.99 s, so 51.3 / 1.99 = 26 W; 18 records |
| Energy of one record | prefill: 0.1305 s x 42 W = 5.5 J, **21% of the phase**; decode: 0.1305 s x 26 W = 3.4 J, 6.6% |
| Joules per millisecond of timing bound | prefill 0.047 J/ms; decode 0.041 J/ms (each run's attribution bound divided by its timing bound) |
| Attribution floor at the block-3 operative bound of 45.7 ms | prefill 45.7 x 0.047 = **2.1 J (8.0%)**; decode 45.7 x 0.041 = **1.9 J (3.7%)** |
| Run-to-run scatter of the prefill phase | standard deviation 0.38 J (1.5%) |
| The "1% class" used by the published benchmarks (section 6) | prefill 0.26 J; decode 0.51 J |

Why the floor is as large as 8%, in one picture. A prefill phase is 0.62 s long and the sampler only reports
averages over 0.13 s, so the phase is covered by about five records and each edge of the phase falls
somewhere inside one record:

```
records (each = average power over 130.5 ms; 5.5 J each at 42 W)
   |  r1  |  r2  |  r3  |  r4  |  r5  |  r6  |  r7  |
          ^                                ^
     phase start                       phase end        (0.62 s apart)
       <-->                              <-->
   timing bound b_op (45.7 ms): where each edge may really be
```

Named elements: `r1`..`r7` are consecutive records; the two carets are the phase boundaries as stamped by the
workload; each double arrow is the timing bound, the stretch within which the true edge may lie. Sliding both
edges by 45.7 ms moves 45.7 ms x 0.047 J/ms = 2.1 J in or out of the phase. That is the floor, and it cannot
be averaged away by repeating runs, because every run is laid on the timeline by the same method.

The owner's worry was "1 J on a 1 MJ workload". That case does not occur here because the workloads are small:
1 J is 3.8% of a prefill and 1.9% of a decode. The disproportion found is the opposite kind: boundaries that
guard a few hundredths of a joule and have nevertheless stopped whole sessions.

## 2. One row per boundary

Columns. **Guards**: the error the boundary exists to prevent. **Present**: the block-5 value and what
crossing it does. **Error at the boundary**: joules, then percent of a 26.1 J prefill and of a 51.3 J decode.
**Cost so far**: what block 5 lost to it (attempts and runs; counts of flagged runs are blinded and written
"unknown"). **Published practice**: MLPerf Power, SPECpower_ssj2008 and JouleSort (section 6). **Proposed**:
the value or mechanism for the next block, with its arithmetic. IDs are the audit's.

| ID | Boundary | Guards | Present | Error at the boundary | Cost so far | Published practice | Proposed for the next block |
|---|---|---|---|---|---|---|---|
| T1 | Alignment screen on each alignment capture | The timing bound that sets the attribution floor | 36.46 ms, the largest of 24 good captures. An opening capture above it stops the session before any run | 1 ms over adds 0.047 J = 0.18% of prefill, 0.041 J = 0.08% of decode. 5 ms over: 0.24 J = 0.9%, 0.21 J = 0.4% | BETA attempt 3: session stopped, zero runs. 3 of 52 captures on record exceed it (5.8%; 4% expected by construction) | MLPerf: a fixed clock tolerance of 800 ms between its two machines, far above ordinary offsets. SPECpower, JouleSort: none | **Flag above 36.46 ms and carry the capture's own bound into `b_op`.** Stop only above 60 ms. Arithmetic: 60 ms is 8.4 standard deviations (3.8 ms) above the median of 27.9 ms; at 60 ms, `b_op` = 60 + 14.5 = 74.5 ms and the floor is 74.5 x 0.047 = 3.5 J (13% of prefill), 3.1 J (6% of decode), still under the 25% limit of T10 |
| T2 | Movement between the opening and closing capture | Alignment changing during the session | max(change, 14.531 ms) must not exceed 15.502 ms; else the session is removed | Same rate: 1 ms over adds 0.047 J = 0.18%, 0.041 J = 0.08% | None | None of the three | Same treatment as T1: the change is already inside `b_op`; flag above 15.502 ms, remove only where `b_op` passes the T1 stop (74.5 ms) |
| T3 | Clock bound of one run | The whole record sequence of a run sitting wrong on the clock | 5 ms; above it the run is not used | 5 ms x 42 W = 0.21 J = 0.8%; 5 ms x 26 W = 0.13 J = 0.25% | 2 of 520 runs; no session | MLPerf: 800 ms on a run of 600 s, 0.13% | Keep 5 ms as the flag level. Remove a run only above 15 ms, the backstop the code already has: 15 ms x 42 W = 0.63 J = 2.4%; x 26 W = 0.39 J = 0.75%; both under the floor |
| T4 | Clock-rate check before a session starts | Predicts T3 for the longest sampler stream (335 s) | 3.7 ms + (rate + 0.25 ppm) x 335 s must not exceed 5 ms, so the clock's rate correction must be within 3.63 parts per million (ppm) | 0.1 ms over is 0.004 J | No refusal. Margin at the last start: 0.31 ms, which is 0.9 ppm | None of the three | Size it to T3's removal level: (15 - 3.7) ms / 335 s - 0.25 = 33.5 ppm. The present 3.63 ppm stays as a flag level. A physical clock-drift refusal remains; it sits where the error reaches 0.6 J, not 0.004 J |
| T5 | Clock jump inside a run | The no-jump assumption the timing bound is built on | 1 ms between one-second samples; flags the run | 1 ms x 42 W = 0.04 J, but the real harm is that the bound stops being true | None | MLPerf: stop time-sync daemons, sync once before the run | **Keep.** Named hazard: it invalidates the printed uncertainty |
| T6 to T9, T11 | Sampler and fit validity (60 s of stream, at least 3 records in a phase, phase at least 2 record-lengths, sampler interval at most 150 ms median) | That a phase can be integrated at all | Margins of 2x to 6x on the two target phases | Not energy sizes; they mark where the estimator stops | No session; run counts unknown | SPECpower: at least 1 reading per second on a 240 s interval | **Keep.** They are estimator limits |
| T10 | Attribution bound against the phase energy | That a reported number is not mostly uncertainty | Bound at most 25% of the phase energy | 25% of 26.1 J = 6.5 J; of 51.3 J = 12.8 J | Unknown | 1% instrument uncertainty | **Keep.** It is this note's rule in its bluntest form, and it sets the ceiling for T1: 6.5 J / 0.047 J/ms = 139 ms of `b_op` |
| Q1 | Contention: any one outside process | Another process's energy counted as the model's | 0.05 CPU-s/s (5% of one core) per process. Before the start: wait for 180 s clean. In a run: the run's unit is removed | Assumed 4 to 6 W per busy core, so 0.2 to 0.3 W. 0.3 W x 0.62 s = 0.19 J = 0.7%; x 1.99 s = 0.6 J = 1.2% | First-seal ALPHA attempt 2 (start refused, cheap). Runs unknown | None has a per-process limit; all three rely on a dedicated machine and repeats | **Size it in watts, summed over outside processes, in two tiers.** Flag at 0.25 W (1% of the decode's 26 W; 0.16 J = 0.6% of prefill, 0.5 J = 1.0% of decode). Exclude at 1.0 W, the same line as Q2 (0.62 J = 2.4%; 2.0 J = 3.9%, the size of the decode floor). The CPU-s/s limit is then watts / (measured watts per core), section 3.3 |
| Q2 | Idle admission: processor power | The machine being quiet just before the request | p95 at most 1.0 W over the 75 s idle baseline; one immediate retry, then the run is aborted | If 1 W carried into the request: 1.0 x 0.62 = 0.62 J = 2.4%; 1.0 x 1.99 = 2.0 J = 3.9%. Quiet idle is 0.05 W, so the line is 20 times quiet | **The largest.** First seal: ALPHA attempts 1 and 3 lost (with N2). Second seal: 2 of 125 runs (ALPHA 1), 8 (BETA 1; `RUN_STATE.md` item 14 puts five on a 20-minute malware scan), 4 in 25 minutes (BETA 2; item 17 puts three or four on the daily maintenance batch) | SPECpower: 30 s settle before and after each 240 s interval, idle measured as a level. MLPerf, JouleSort: none | **Value unchanged; the mechanism waits instead of aborting** (section 3.1): slide the 75 s baseline until it passes, up to 1,500 s |
| Q3 | Idle admission: processor busy fraction | Same | p95 at most 0.5 | Not convertible to joules. A quiet baseline read 0.469 (6% margin) | Inside Q2's counts | None | **Flag only.** Q2 measures the watts directly; this is a proxy for the same thing with no stated link to energy |
| Q4 | Agent census | An assistant process loading many cores | Any such process stops the session | Rehearsals with agents alive read 8 to 47 W at "idle": 19% to over 100% of a phase | BETA attempt 2 | Dedicated machine | **Keep** |
| Q5 | Thermal state | Throttling | Operating-system level 0 | Binary | None | SPECpower: ambient at least 20 °C, read 4 times a minute | **Keep** |
| Q6 | Battery current | Charging, or running from the battery | 200 mA at the start; a run above +200 mA is removed | 200 mA x 12.2 V = 2.4 W at the battery; it does not enter the processor rails directly, so it has no joule size here | None at the start; runs unknown | MLPerf: no battery before the power supply at all | Keep as it is; section 4 lists the test that would give it a size |
| S1 | Sleep during a session (new; `RUN_STATE.md` item 19) | A hole in the records and a different machine state | Not registered. Desk check after each session: the sleep-blind clock and the sleep-counting clock may not part by more than 0.1 s | A sleep inside a run breaks its record sequence: validity, not a joule size | BETA attempt 4: asleep 3,507 s of 25,049 s | None | **Register it per run**: the two clocks' difference is read at each run's start and end; a change above 1 ms flags the run (a session with no sleep read 2.5 µs, so 1 ms is 400 times the quiet reading; 1 ms x 42 W = 0.04 J). The driver holds a no-sleep assertion itself |
| N1 | Drift screen | The instrument reading differently at the end of a session than at the start | End mean minus start mean within a bound from the corpus; 0.98 J in the rehearsal | 0.98 J is 2.7% of the 36.8 J reference. Each run carries half: 0.49 J = 1.9% of prefill, 1.0% of decode | The number has removed nothing | MLPerf: mean power of the measured run may not be more than 5% below its range-finding run. JouleSort: 5 runs, report the standard deviation | **Keep.** Sized from the session's own data and tighter than MLPerf's 5% |
| N2 | Corpus minimum | Precision of N1's bound | At least 10 corpus runs survive, else the session is removed | The bound's small-sample multiplier (Student's t, 97.5th percentile) is 2.262 at 10 runs, 2.365 at 8, 2.571 at 6. On its 0.71 J term: +0.03 J at 8, +0.10 J at 6: 0.1% to 0.4% of prefill | **First-seal ALPHA attempts 1 and 3** (5.3 h and 5.5 h). Cured by planning 18 | SPECpower: at least 3 calibration intervals. JouleSort: 5 runs | **Minimum 6, bound computed at the count that survives.** At 6 the bound widens by 0.10 J (0.4% of prefill, 0.2% of decode), carried in the bound. One unreadable corpus run is dropped and flagged, not fatal |
| N3 | Reference minimum | A start-to-end difference existing at all | At least 2 start and 2 end references | Structural | BETA attempt 1, through a missing record (cured prospectively by Erratum 2) | JouleSort: 5 runs | **Keep** the count; a missing record about a reference is a flag |
| N4 | Units per stratum | The estimator being defined | At least 5 of 10 | At 5 the interval is 1.74 times wider; still honest | Only sessions already cut short | JouleSort: 5 | **Keep** |
| N6 | Fixed start-to-end comparison in the policy file | Same as N1 | 0.05 J and 25%, still read by the code | 0.05 J is 0.14% of the 36.8 J reference and an eighth of its 0.40 J repeat scatter | None known; whether it can fail a session is not traced | None | **Remove the fixed 0.05 J from the next policy file**, or set it from N1's derived bound. Trace first (section 4) |
| L2 | Free disk at the start | Lost bytes | 3 copies of the planned bytes + 20 GiB = 90.4 GiB | Not an energy | None | None | Size to what is written: 23.5 + 20 = 43.5 GiB. No cost today, so low priority |
| R1 | Runs per session | The interval on each reported mean, and surviving lost runs | 125 (100 science runs, 18 corpus, 7 references) | 10 repeats give a half-width of 2.262 x 0.38 / sqrt(10) = 0.27 J = 1.0% of prefill: an eighth of the floor | 9.2 h per session on the block-3 basis | MLPerf: 1 range-finding + 1 measured run of 600 s. SPECpower: one pass. JouleSort: 5 runs | **99 runs (8 units per stratum, corpus 12), decided after block 5 is unblinded** (section 3.5) |
| C1 | Time-server offset reading (new) | A wall-clock jump or rate fault nothing else sees | Not done; network time is OFF during a session | A 0.1 s jump inside a run would be up to 0.1 s x 42 W = 4.2 J | None: no attempt was lost to the clock | MLPerf: sync once before the run, daemons stopped | **Query-only reading before and after each session, network time still OFF; a flag** (section 3.4) |

Reading the table as a whole: the two columns "Error at the boundary" and "Cost so far" should rise together.
In block 5 they did not. Of the seven failed attempts whose cause is in this note's inputs (BETA attempt 5 is
not covered by them), none was removed by a
measured energy drift, a clock fault, a thermal state or the battery. Two were removed with N2 behind them
(0.03 to 0.10 J), one by T1 (0.05 J per millisecond over), one by a missing record, one by a cheap refusal at
the start (Q1), one by a real hazard (Q4, an assistant session at the keyboard), and one by a sleeping
machine that no registered check could see.

## 3. The mechanism changes

### 3.1 Idle admission waits instead of aborting (Q2, Q3)

*Forcing problem.* The reported energy is gross: no idle power is subtracted from it. So the quietness of the
idle baseline enters no reported number. The baseline is only a predictor that the request, a few seconds
later, will run on a quiet machine. The present rule treats a failed prediction as a failed run: one
immediate retry, then the run is aborted, and its quad loses a unit. But the disturbances that failed it in
block 5 were long and known: a malware scan of 20 minutes at about two cores (item 14), the once-a-day
maintenance batch of about 12 minutes at one to two cores (item 17), and the midnight cleaner, 51 s at a third
of a core (item 29). An immediate retry inside a 20-minute scan must fail. The same rule is also too eager in
the other direction: 5% of 576 records is 29 records, 3.8 s, so one 4 s burst early in the baseline aborts a
run although the burst ended more than a minute before the request.

*Mechanism.* Keep the limit (p95 at most 1.0 W over 576 consecutive records). Change what failing does:

```
time ->
 |--- baseline 1 (75 s) ---|   fails: p95 = 6 W (scan running)
        |--- baseline 2 ---|   the 576-record span slides forward as new records arrive
                 ...            (sampler keeps running; nothing is restarted)
                      |--- baseline k (75 s) ---|  passes: p95 = 0.3 W
                                                 |warm-up|request|
 |<-------------- wait, at most 1,500 s ------------------------>|
```

Named elements: each bar is one 576-record span of idle processor power; "slides forward" means the test is
re-evaluated on the most recent 576 records each time a record arrives; the wait is the time from the first
baseline's start to the first passing span; warm-up is the short model execution that already precedes every
request.

*Worked numbers.* The cap is the longest known disturbance plus one full baseline plus margin: 20 minutes
(1,200 s) + 75 s = 1,275 s, rounded up to 1,500 s. On the cap being reached the run is skipped and flagged,
and the session continues. Had this been in force, the scan of 10-10 would have cost BETA attempt 1 about
20 minutes of waiting where it cost five runs of one stage, and the batch about 12 minutes where it cost three
or four runs. Worst case for the session length: each of the three daily disturbances met once is about
33 minutes of added wait against a session time limit of 27 to 31 hours.

*What it retires.* The start-time preferences of items 14, 17 and 29 (avoid 05:15 to 06:45, 12:45 to 13:10 and
midnight) exist only because a disturbance costs runs. With a wait they cost minutes, and the rule "pick a
start time whose chain misses these hours" can go.

*Q3.* The busy-fraction test becomes a recorded flag. It is a second reading of the same hazard with no link
to joules, and its margin on a quiet machine is 6%.

*What stays open.* A longer idle before a run means a cooler chip at the warm-up. Whether that moves the
phase energy is not measured; section 4 gives the test.

### 3.2 The alignment screen becomes a flag, and the bound is carried (T1, T2, T3, T4)

*Forcing problem.* An alignment capture above 36.46 ms does not make any number wrong. The capture's own value
enters `b_op`, and `b_op` sets the printed floor. Worked: an opening capture of 37.5 ms in place of 36.46 ms
raises `b_op` by 1.04 ms and a 2.1 J floor by 1.04 x 0.047 = 0.049 J. The fixed 14.5 ms already inside `b_op`
is worth 14.5 x 0.047 = 0.68 J, fourteen times that. Yet crossing the line stops the session before a single
run, and because the line is the largest of 24 captures, a good capture crosses it 1 time in 25. A session has
two captures, so about 1 session in 13 is stopped or removed with nothing wrong.

*Mechanism.* Three bands for a capture's timing bound `c`:

1. `c` at most 36.46 ms: as today.
2. 36.46 ms < `c` at most 60 ms: the session runs. The flag `alignment_above_reference` is recorded with `c`,
   and `c` enters `b_op` unchanged, so the result prints a larger floor.
3. `c` above 60 ms: the session stops. This is the physical line: a sampler in a different state (the faulty
   launch context of September gave records of 244 to 250 ms where 130.5 ms is normal).

The 60 ms line is a proposal to be sized by the council, between two fixed points: it must sit well above the
tail of good captures (the acceptance's own extended range reaches 42.6 ms) and below the point where T10
would refuse every prefill, 139 - 14.5 = 124 ms. The one number that would test the proposal against block 5
is the value of BETA attempt 3's opening capture, which is a calibration time and not an energy, and which
this note did not read.

The clock bound of a run (T3) and the rate check that predicts it (T4) follow the same reasoning with one
difference: clock drift beyond budget is a physical hazard and keeps its refusal. Only the budget moves, from
the point where the error is 0.21 J (5 ms) to the point where it is 0.63 J (15 ms). The reason to do it is the
margin, not past cost: the last start passed by 0.31 ms, and the stored rate correction is rewritten by every
clock resync (it read -3.17 ppm on 10-05 and +2.72 ppm on 10-10). A change of 0.9 ppm would refuse every
start over an error of 0.004 J per 0.1 ms.

### 3.3 The contention limit is sized in watts (Q1)

*Forcing problem.* The limit is "5% of one core, per process". Energy does not care which process spent it or
what fraction of a core that was; it cares about watts times seconds. Three things follow.

1. The same hazard is guarded at two different lines. Idle admission accepts up to 1.0 W of outside power;
   the contention rule removes a run for one process at an assumed 0.2 to 0.3 W.
2. Per-process counting misses the sum. Ten processes at 4% each pass; one at 6% fails.
3. The watts are assumed. The audit used 4 to 6 W for one busy performance core. That cannot hold for light
   background work: the background daemons seen on this machine sit at about 0.03 CPU-s/s each, yet the whole
   processor reads 0.05 to 0.06 W in a quiet baseline, which is under 2 W per busy core for that kind of
   work, not 4 to 6. (The two readings are from different days, so this is an inference to be measured.)

*Mechanism.* State the limit as outside power in watts, summed over all outside processes, over the same 10 s
intervals as today. Convert to the measured quantity with a measured factor `w` (watts per CPU-second per
second, from the test in section 4):

- **Flag** at 0.25 W, which is 1% of the decode's 26 W: 0.25 x 0.62 = 0.16 J (0.6% of prefill),
  0.25 x 1.99 = 0.50 J (1.0% of decode). With `w` = 5 W this is 0.05 CPU-s/s, so today's value survives as the
  flag level if the assumption holds.
- **Exclude** at 1.0 W, the idle-admission line: 0.62 J (2.4% of prefill), 2.0 J (3.9% of decode, the size of
  the decode's floor of 1.9 J). With `w` = 5 W this is 0.20 CPU-s/s.

The analysis plan keeps its sensitivity line (each reported mean recomputed with flagged runs left out), so
the reader sees both numbers. Block 5's own sensitivity line, after unblinding, shows directly whether runs
excluded at 5% differ from the rest; that result should be read before the two levels are fixed.

### 3.4 A query-only time-server reading before and after each session (C1)

*Forcing problem.* The energy join never uses the time of day, only the assumption that the wall clock ran at
one steady rate with no jump inside a run. That is why network time is OFF during a session: the operating
system's time daemon is known to jump the clock when it is switched on after a day off (how it corrects once
synchronised is not established on this machine), and a jump under about 0.25 ms inside a run is invisible
to every existing check. With it OFF, nothing outside the machine ever confirms the clock behaved.

*Mechanism.* Before the first run and after the last, ask two time servers for the offset without setting
the clock (`sntp <server>`, no set option), and record the four offsets. Network time stays OFF throughout.

*Worked numbers.* On 10-10 the stored rate correction was 2.72 ppm and BETA attempt 4 lasted 25,049 s, so the
offset should have grown by 2.72e-6 x 25,049 = 68 ms. One query is good to about 30 ms, so a difference of two
is good to about 30 x sqrt(2) = 42 ms. Flag the session when the observed change differs from the predicted
one by more than 100 ms. This sees a jump of 0.1 s or more and gross rate faults; it does not see fine rate.
It is a flag and never a refusal. The queries carry no personal identifier and sit outside every run's
record stream.

This is the published pattern turned around: MLPerf syncs once before a run and stops the time daemons during
it. Here the clock is not even set, only read, because only one machine is involved.

### 3.5 The run count follows from the scatter, the floor and the loss rate (R1)

*Forcing problem.* A session's 125 runs take about 9 hours, and the count of 10 units per stratum is a
convention fixed for feasibility; no calculation stands behind it (`why-125-runs.md` section 2).

*What the scatter says.* With a run-to-run standard deviation of 0.38 J on a 26.1 J prefill, the half-width of
a mean of `n` repeats is t(n) x 0.38 / sqrt(n), where t(n) is the small-sample multiplier:

| Units `n` | Multiplier | Half-width | Percent of prefill | Share of the 2.1 J floor |
|---|---|---|---|---|
| 10 | 2.262 | 0.27 J | 1.0% | 13% |
| 8 | 2.365 | 0.32 J | 1.2% | 15% |
| 6 | 2.571 | 0.40 J | 1.5% | 19% |
| 5 | 2.776 | 0.47 J | 1.8% | 22% |

So at 10 units the statistical uncertainty already meets the published 1% class, and at every count down to 5
it is under a quarter of the floor that is printed beside it. For the reported means, more runs do not buy a
better printed number; the floor does not shrink with repeats.

*What the count is really for.* Surviving lost runs. A unit is lost when any of its runs is lost, and below 5
units a stratum has no defined estimator. At the one measured loss rate (1 run in 37, all idle-admission
aborts) the chance that all four strata of a session keep 5 units is 0.9996 with 10 planned and 0.988 with 8.
If waiting (3.1) cuts the loss rate to 1 in 100, the 8-unit figure becomes 0.9997.

*Proposal.* 8 units per stratum and a corpus of 12 (enough once N2's minimum is 6 and corpus runs are no
longer aborted): 12 + 7 + 2 x (8 + 32) = 99 runs, about 7.5 h on the block-3 basis, 21% fewer runs. Intervals
widen by 2.365 / 2.262 x sqrt(10 / 8) = 1.17. Two conditions, both checkable only later: the loss rate under
the waiting mechanism is measured in a rehearsal, and the two-model contrast in block 5, once unblinded, sits
well above its detection floor (wider intervals could otherwise turn "resolvable" into "not resolvable"). If
either fails, 10 units stay. The larger saving is elsewhere: about 230 of each run's 237 s are waits.

Against published practice: 50 runs per reported mean x 0.62 s = 31 s of prefill signal, and 50 x 1.99 s =
100 s of decode. MLPerf's own paper gives 60 s as its minimum measured duration. The repeats here do the job
that one long run does there.

## 4. Assumed, not measured, and the cheap test for each

| # | Assumption in this note | Where it is used | Test | Cost |
|---|---|---|---|---|
| 1 | One busy core costs 4 to 6 W | Q1's joule size; the factor `w` | A synthetic process that keeps one core 5% busy, for 60 s, once at background priority (efficiency cores) and once at interactive priority (performance cores); read processor power against a 60 s idle. Repeat at 20% and 100% | 10 minutes, quiet machine |
| 2 | Quiet background daemons cost under 2 W per busy core | Section 3.3, point 3 | Same session as test 1: per-process CPU-s/s and processor power from one 75 s idle baseline, same instant | Inside test 1 |
| 3 | BETA attempt 3's opening capture was the ordinary tail | T1 | Read that one calibration time (not an energy) under whatever gate allows it; compare with 36.46, 42.6 and 60 ms | Minutes |
| 4 | A closing capture over the screen removes a finished session | T1's "1 in 13" | Trace the closing path from the capture classifier to the harvest's reason code | Code only |
| 5 | The fixed 0.05 J comparison cannot fail a block-5 session | N6 | `joulewise/idle_admission.py` lines 673 to 676 set a condition that makes the bracket decision "failed"; trace whether the block-5 harvest reads that decision | Code only |
| 6 | The 8B phase energies are "roughly 300 to 400 J" | Any 8B percentage | Block 5's own values after unblinding. The only 8B rehearsal ran on a loaded machine | None |
| 7 | Drift adds the same joules to a large run as to a small one | N1 applied to the 8B pack | Two start and two end references of the 8B workload in the next 8B session; compare their drift with the small reference's | 4 runs, about 16 minutes |
| 8 | A longer idle before a run does not change its phase energy | 3.1 | 10 reference runs after the normal 85 s idle and 10 after a 20-minute idle, alternated | About 4 hours, mostly idle |
| 9 | The loss rate falls under the waiting mechanism | 3.5 | One rehearsal session with the new admission across 12:53 and one scan hour | One session |
| 10 | The decode's run-to-run scatter is like the prefill's 1.5% | 3.5's table (prefill only; the rehearsal has 6 decode runs) | Tabulate from the next rehearsal with at least 20 decode runs | None extra |
| 11 | One time-server query is good to 30 ms | C1's 100 ms flag | Ten queries to two servers over 10 minutes; read the scatter | 10 minutes |
| 12 | The busy-fraction statistic adds nothing to the 1.0 W test | Q3 | Its distribution over the 53 quiet rehearsal baselines; after unblinding, whether any block-5 abort failed on it alone | Minutes |
| 13 | The processor rails read true watts | Every joule in this note | Compare the rails with the wall meter (connected 2026-09-23) over a steady loop of 60 s or more. It needs a battery state in which the charger carries the load: on 09-23 the battery supplied 439 mA at 100% charge while the meter path read about 0 W | Half a day, including finding that state |
| 14 | Battery current under 200 mA does not move rail readings | Q6 | Reference runs at three forced battery states (floating, slight charge, slight discharge) | One short session |
| 15 | 60 ms separates a good sampler from a disturbed one | T1's stop line | Alignment captures taken on purpose under the faulty launch context and under one core of load | 1 hour |

Tests 1, 3, 5 and 11 are cheap enough to run before the council sits, and each replaces an assumption in a
proposal the council would otherwise argue from.

## 5. Who decides what

The next block's registration and analysis plan pass a cold gate as a whole before the seal; that is
unchanged. The question here is which proposals need a council's answer before they are written into the
draft, and which the orchestrator simply writes.

**Two-seat council first (a science question: the choice changes which data count or what uncertainty is
printed).**

1. T1 and T2: flag-and-carry, and the size of the stop line (60 ms proposed; fixed points 42.6 and 124 ms).
2. Q1: watts in place of percent of a core, summing over processes, and the two levels (0.25 W, 1.0 W). After
   test 1 and after block 5's sensitivity line is unblinded.
3. Q2 and Q3: waiting in place of aborting, the 1,500 s cap, the busy fraction as a flag. Test 8 bears on it.
   `RUN_STATE.md` item 17 already names a cold gate for this proposal if the cause recurs.
4. T3 and T4: moving the removal level from 5 ms to 15 ms. The 5 ms is part of the claim method's stated
   identity, so this also needs the cold gate named below.
5. N2: corpus minimum 6 and the bound at the surviving count.
6. R1: 99 runs. After unblinding and test 9.

**Cold gate in its own right (beyond the registration's own gate).**

- T3/T4, because the clock cap belongs to the identity of the timing method the claims rest on.
- The analysis-plan clause that names which flags exclude a run or a session from a claim. Every refusal
  turned into a flag in this note moves a decision from collection time to that clause, so the clause is
  where the science is now protected, and it is fixed before any data exist.
- Any of the above applied to block 5 itself. Nothing here is proposed for block 5.

**The orchestrator's call, recorded in the session record.**

- Stating every boundary in joules and percent in the registration (section 1's three-way form).
- C1, the time-server reading, as a flag. It refuses nothing.
- S1, the per-run sleep reading as a flag, and the no-sleep assertion in the driver. (A registered session
  reason for sleep is already an open erratum lane, item 22(a).)
- N6: removing the fixed 0.05 J from the next policy file, after test 5.
- L2: the disk figure.
- N3: a missing record about a reference becomes a flag.
- Running tests 1 to 5 and 10 to 12 of section 4, and retiring the start-time preferences once 3.1 is in.
- Reporting the energy of one record (5.5 J, 21% of a prefill) beside the attribution floor in the paper.

## 6. What the published benchmarks do, and what transfers

Three rule sets were compared: **MLPerf Power** (Tschand et al., arXiv:2410.12032, and the MLCommons
power-measurement rules and compliance checker), **SPECpower_ssj2008** (Run and Reporting Rules), and
**JouleSort** (Rivoire, Shah, Ranganathan and Kozyrakis, SIGMOD 2007; rules as given in the Sort Benchmark
FAQ). A research seat read them; the orchestrator re-read three sources directly to check the numbers marked
"checked".

| Item | MLPerf Power | SPECpower_ssj2008 | JouleSort | Here |
|---|---|---|---|---|
| What is measured | Whole system at the wall | Whole server at the wall | Whole system at the wall | Processor power rails, read on-chip |
| Instrument accuracy | 1.00% per sample, else the run fails (checked) | 1% overall, calibrated within a year, crest factor at least 3 (checked) | within 1% (checked) | No published accuracy for the rails (section 4, test 13) |
| Reading rate | about 1 per second | at least 1 per second (checked) | at least 1 per second, equally spaced (checked) | 1 per 130.5 ms |
| Length of one measurement | 60 s minimum in the paper; 600 s in the inference run rules | 240 s per load level, 30 s before and after (checked) | The sort's own length | 0.62 s and 1.99 s |
| Repeats | 1 range-finding run + 1 measured run | One pass | 5 consecutive runs; mean and standard deviation (checked) | 50 runs per reported mean |
| Drift check | Measured-run mean power not more than 5% below the range-finding run (checked) | None | The standard deviation of 5 | Two-sided, 2.7% of the reference, from the session's own corpus |
| Clock | 800 ms tolerance between two machines (checked in code; the checker's own documentation says 200 ms) | Not stated | Not stated | One machine; 5 ms per run; network time OFF |
| Idle | None | Measured as a level | None | Admission test, 1.0 W |

Two corrections to the research seat's report from the re-read: the checker on the main branch today accepts
measurement-daemon version 1.11.1 (the report said 1.9.1 and 1.9.2), and its list of supported meters
includes direct-current variants of three analyzers, so "alternating current at the wall only" is no longer
the whole of MLPerf's boundary. Not read by anyone: MLPerf's best-known-methods document (where ambient
limits probably are), the JouleSort paper's full text, and SPEC's server-efficiency tool (SERT).

**What does not transfer.** A minimum run of 60 or 600 s, reading once a second, and an 800 ms clock tolerance
all assume a measurement hundreds of seconds long. One reading there is 1/600 of the result, 0.17%. One record
here is 21% of a prefill. An 800 ms tolerance is longer than the whole prefill. Range-finding and crest factor
belong to wall meters. And the wall boundary conflicts with the battery rule: the project holds the battery
full and idle, and in that state the wall path can read about 0 W while the battery supplies the machine.

**The three lessons that change something here.**

1. **A tolerance belongs well above the ordinary spread, and crossing it should cost in proportion.** MLPerf's
   clock tolerance is a round engineering value hundreds of times its usual offsets (and its code and
   documentation disagree on it, 800 against 200 ms, which shows it is tuned and not derived). The alignment
   screen here was drawn at the largest of 24 good values and stopped a session over 0.05 J per millisecond.
   This is T1, and the rule's last sentence in section 1.
2. **Where a published benchmark handles a disturbed machine, it settles and waits; it does not discard.**
   SPECpower puts 30 s before and after each interval. None of the three aborts a measurement because the
   machine was busy before it began. This is 3.1, the change with the most lost runs behind it.
3. **All three benchmarks state an instrument accuracy of 1%, and the project states none for its rails.**
   Every threshold in this note is sized in joules read from an instrument whose absolute accuracy is
   unmeasured. The floor bounds timing only. A comparison of the rails with the wall meter over a long steady
   loop (section 4, test 13) is the one new number the comparison says is missing, and until it exists the
   paper's threats section has to say that these energies are not comparable with wall-measured figures.

A fourth point supports leaving something alone: on run count, the project's 31 s and 100 s of accumulated
signal per reported mean are of the same order as MLPerf's 60 s minimum, its drift screen is tighter and
two-sided, and network time OFF with one machine is MLPerf's own pattern (daemons stopped during the run)
with less to synchronise.

## 7. Identifier glossary

For a reader moving between this note and the code or the sealed registration: "window" there means session
(`window_id`, `whole_window.py`, `WINDOW_MAX_S`) or interval (`window_class`, `window.start_s`); "member" means
run; `systematic-invalid` is the alignment screen's verdict (T1); `calibration.bracket_acceptance_failed` is
T2; `member.anchor_not_bounded` is T3; `clock.step_overlap` is T5; `contention.request_overlap` is Q1;
`neg8.screen_failed` and `neg8.bound_not_derived` are N1/N3 and N2; `cell.below_minimum` is N4. None of these
identifiers is renamed by this note.

## 8. Council outcome (2026-10-12)

Two seats read this note blind to each other: Fable 5.1 and Sol 6.1 (reports
`/Users/edr/night-archive/b5-consults/threshold-council/seat-fable.md` and `seat-sol.md`). Each re-derived the
arithmetic. The orchestrator (Opus 5.5) decides below. Nothing here is adopted until the next block's
registration passes its cold gate; "measure first" rows go to the quiet-machine list of section 8.2.

**A correction to this note.** Section 3.2 says the operative bound at the proposed 60 ms stop line would be
74.5 ms. Both seats reject that figure. With an opening capture at 60 ms and an ordinary closing capture of
28 ms the operative bound is about 60 + 32 = 92 ms, which is a floor of about 4.4 J on a 26.1 J prefill
(16.7%). The 60 ms line is therefore not a proposal any more; see T1.

### 8.1 Decisions

| Row | Fable 5.1 | Sol 6.1 | Decision |
|---|---|---|---|
| T1 flag above 36.46 ms and carry the bound | adopt | adopt the flag | **Adopt the flag.** Crossing the screen changes no number; the capture's value enters the operative bound. |
| T1 stop line | one stop on the operative bound, not on the capture | cannot be derived from ordinary captures | **Measure first** (test 15, extended: captures on a quiet machine, under one core of load, and under the faulty launch context). One line, on the operative bound, sized from that data. |
| T2 capture-to-capture movement | adopt as a flag | flag; drop the 74.5 ms ceiling | **Adopt as a flag.** |
| T3 run clock bound | 15 ms removes, 5 ms flags | 15 ms as the total effective bound, placement kept at 5 ms | **Sol's form.** The reducer charges the clock span at both edges, so 15 ms of span alone can cost 1.58 J on a prefill (6%), not 0.63 J. Total effective bound 15 ms; placement 5 ms. |
| T4 rate check | 25 ppm | recompute for the longest admitted stream | **Derived after Q2's cap is known**, as (15 ms minus placement) over the longest stream; no free value. |
| Q1 contention in watts | measure first | measure first | **Measure first** (test 1, plus phase-length bursts at several placements inside the ten-second accounting interval: 1 W averaged over ten seconds allows 10 J inside one phase). |
| Q2 idle admission waits | adopt, cap interim | mechanism yes, cap and thermal effect unmeasured | **Adopt the mechanism.** The cap comes from the recorded lengths of past disturbances, and a paired test (ordinary wait against long wait) must show the cold-machine effect is under the floor before the seal. |
| Q3 busy fraction | flag | flag | **Adopt as a flag.** 13 of 53 quiet rehearsal baselines fail it while their power is 0.17 to 0.42 W against a 1.0 W limit. |
| S1 sleep | flag, plus a reading between runs | exclude a run that slept | **Both.** A run in which the machine slept more than 1 ms is excluded; the cumulative sleep reading is also taken at every run start and recorded, which sees sleep between runs. |
| N2 reference-corpus minimum | 6 | 6 | **Adopt 6**, the bound computed at the surviving count. |
| N6 fixed 0.05 J comparison | trace, then remove | retire | **Trace (test 5), then retire.** |
| R1 runs per session | keep 10 units until decode scatter is measured | measure first | **Keep 10 units per stratum.** Revisit when block 5 is unblinded and gives the scatter per stratum. |
| C1 time-server reading | flag at 100 ms | threshold unmeasured | **Record it as a diagnostic from the next session on; no threshold until test 11 gives the query scatter.** |
| L2 free disk | keep 90.4 GiB | measured writes plus 20 GiB | **Measured writes of the largest session plus 20 GiB** (the hazard measured directly; 43 GiB kept per session so far gives 63 GiB). |

### 8.2 What both seats found that this note missed: boundaries that are too loose

This note looked for strictness. The seats were asked to look the other way and found three gaps.

1. **Nothing bounds a run's duration or token rate.** Anything that slows the model adds its own power for
   the extra time: a decode 10% longer at 26 W adds about 5.2 J, and no watt or processor-time rule sees it.
   The rehearsal's prefill duration varies by 1.2% (one standard deviation), so a flag at three standard
   deviations costs almost nothing. Proposed for the next registration as a flag.
2. **Contention is counted in processor time only.** A process working on the graphics processor or the
   neural engine adds power to the measured rails with little processor time. A 10 W contender would add
   6.2 J to a prefill and 19.9 J to a decode. Both seats raised this independently. The photo and media
   analysis agents are of this kind; they are disabled from the next login (RUN_STATE item 35 (d)). The
   measurement: read the graphics-processor power rail in the idle baseline and during a run of a
   processor-only reference workload, and size a limit on it.
3. **The reducer's handling of a record that straddles a phase edge** (Sol's finding F5). A power record is
   an average over about 130 ms. The reducer gives a phase the share of a record's energy equal to the share
   of the record's time inside the phase. For a synthetic 42 W rectangle of 0.62 s with nothing outside it,
   the seat got 23.64 J with an upper bound of 25.13 J against 26.04 J constructed. Whether this reaches a
   number the paper prints, and whether the printed uncertainty covers it for the real shapes, is under
   investigation (`threshold-council/F5-investigation.md`); the outcome is recorded in RUN_STATE.

### 8.3 Quiet-machine measurements (for the headless orchestrator; no agent session alive while they run)

Tests 1, 11 and 15 of section 4, with the extensions named in 8.1; the phase-length burst test for Q1; the
paired ordinary-wait and long-wait test for Q2; the graphics-processor rail reading of 8.2 item 2; and the
rails-against-wall-meter check of section 6 (a steady load of 60 s or more, in a battery state where the
charger carries the load). None of them is a claim session: no registration, no seal, results to
`/Users/edr/night-archive/threshold-validation/` with a short record on the records branch.
