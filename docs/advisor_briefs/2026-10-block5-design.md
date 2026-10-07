<!-- Origin: item 24 of the 2026-10-07 paper wave. Written against revision 9 (DRAFT, not sealed) of the
     block-5 registration, its analysis plan and its flag catalog, as they stand in this tree under
     configs/campaigns/v5_claim_25g83/. Every registered number below carries an HTML comment naming the
     section and line it was read from ("src:"), or the arithmetic that produced it ("calc:"), so that the
     sync after the seal can recheck each one mechanically. Line numbers are those of the files at commit
     9b0c680ed. No measurement from the windows described here existed when this was written, and none was
     read. The plain-language rule for advisor-facing pages applies. -->

# JouleWise advisor brief: the design of the energy measurements for the capstone paper (October 2026)

Audience: the capstone advisor. No project context is assumed beyond this: JouleWise measures how much
energy, in joules, one Apple laptop uses while it runs a language model locally, by reading Apple's built-in
power sampler while the model runs.

**This brief describes a design, not a result.** The measurements it describes have not been collected, and
no number from them exists. Their analysis is blind: until all collection is finished, no energy from them
is shown to anyone, and what decides whether data are kept does not look at the energies of the models
under study (sections 6.3 and 9 give the rule and its one registered exception). Every number below is one
of three kinds, and says which: a *registered* design value (a threshold, a count, a planned duration); a
measurement from an earlier trial or bench test that the design rests on; or a *synthetic* example,
invented to show the arithmetic.

**How to read it.** Section 1 is the whole brief on two pages. Sections 2 to 11 are the detail behind it,
in the same order, for a reader who wants to check a point or challenge a rule.

The design is fixed in three documents: the *registration* (what is collected, and what may stop a
collection or exclude data), the *analysis plan* (what is computed from the collected data, and how) and
the *flag catalog* (a table that says what each kind of recorded anomaly does to the data). They are at
revision 9, in draft. Before the first measurement they are *sealed*: frozen, together with a hash of every
program file a measurement executes, by an independent review. A few values may still change at the seal,
and this brief will be checked against the sealed text once.

## 1. The short version

**What is measured.** A language model reads and writes text in *tokens* (a token is a word or a fragment
of a word). When it answers a request it does two things in turn. It reads the whole prompt and computes
its first output token; this part is called *prefill*. Then it produces the remaining output tokens one
after another; this part is called *decode*. The two parts are the request's *phases*. The quantity
measured is the energy the laptop's processor (its CPU, GPU and neural engine together) uses during each
phase, the *phase energy*, for two models of different size: Qwen3-1.7B and Qwen3-8B, both quantized to
4 bits.
<!-- src: registration §0.4 l.307-309; §0.7 l.392-394 -->

**How strong a sentence may be.** The project writes its results against a *claims ladder*: a written rule
that fixes how strong a sentence may be, given the evidence under it. Two of its rungs matter here.

- **L1, an instrument result:** "on this exact machine, operating-system build, software stack and model,
  this quantity was observed."
- **L2, a comparative result:** "one condition used more energy than another." L2 needs more than L1: both
  conditions measured interleaved inside one stretch of machine time; an interval (a range that expresses
  the uncertainty of the difference) reported with it; and a difference larger than the instrument's
  *detection floor*, which is the largest difference the instrument shows when nothing differs.

The ladder has two higher rungs (a fitted model checked on held-out cases; replication on a second
machine). This design cannot reach them and does not try.
<!-- src: registration §0.19 l.859-863; docs/contracts/claims_ladder.md l.62-65 -->

**Three windows.** A *run* is one request answered by a model in its own process. A *window* is one
unattended stretch of machine time in which one fixed plan of runs executes from start to finish: 119 runs
in each of the first two windows, 101 in the third. A window is expected to take five to nine hours. Three
are planned, in this order:
<!-- src: registration §5.5 l.1848-1852 (member counts; expected chain 4.8 to 9.1 h); §7.2 l.2795 (order) -->

| | Window | What runs | What it can support | Rung |
|---|---|---|---|---|
| 1 | The small-model window (ALPHA in the repository) | Qwen3-1.7B alone | The energy of each phase for this model, with an interval, and this model's detection floors | L1 |
| 2 | The large-model window (BETA) | Qwen3-8B alone | The same for Qwen3-8B | L1 |
| 3 | The comparison window (GAMMA) | The two models interleaved | Two comparisons, Qwen3-8B minus Qwen3-1.7B: one for decode, one for prefill, each judged against the detection floors from windows 1 and 2 | L2 if every registered test passes (section 7.4); otherwise L1 wording |

<!-- src: registration §1 l.877-883 -->

Windows 1 and 2 printed side by side stay at L1. The two models are measured in separate windows in a
fixed order, so the difference between their numbers is not a comparison, and the paper will not present
it as one. Only window 3 compares.
<!-- src: registration §1 l.881; analysis plan §8.1 l.564-565 -->

**What can stop it.**

- *Before a window starts,* a start check refuses to begin for one of three reasons. It measures a
  physical condition that would corrupt an energy (six are checked: the clock, the battery, heat, a
  competing process, meaning other software using the processor, free disk, and the power sampler
  itself). Or it finds an AI coding-agent process running on the machine. Or the operating system has
  been updated to a build on which the instrument's timing was never calibrated. After the start check
  passes, the launch of the runs is itself refused in two more cases (section 4.2): the machine has
  restarted since the launch began, so that timestamps from before and after the restart cannot share
  one time axis; or the plan's sealed list of configuration files cannot be read, so that no run could
  be checked against it. A refusal costs minutes, and the window is tried again when the condition is
  gone.
- *During a window,* a failed run costs only itself. The window as a whole is stopped only if the *timing
  calibration* at its start fails (a test, run before and after each window, of how accurately the power
  readings place a known on/off pattern in time), the disk runs low, an agent process appears, the
  program that records the physical conditions throughout the window falls silent, or the window's time
  limit, its *deadline*, passes.
- *After a window,* nothing is discarded by judgment. Every anomaly is recorded as a *flag*, and the flag
  catalog, sealed in advance, says what each flag does: remove one run, remove the whole window, or be
  reported and nothing more. A window is *claim-usable* when no window-removing flag fired and every
  number to be reported still rests on at least 8 of its 10 planned single runs and 8 of its 10 planned
  groups of four interleaved runs. A window that is not claim-usable is run again as a new attempt. The
  first claim-usable attempt is the one analysed, and attempts are never mixed.
- *All collection stops* if, for more than half of all runs so far, the position of the sampler's power
  readings on the machine's clock cannot be pinned down to within 5 ms. The timing instrument is then
  failing, and running again cannot cure it.

<!-- src: registration preamble l.32-40; §0.15 l.750-753, l.758-760; §0.17 l.809-814 (the two launch refusals); §5.1 l.1543-1549; §7.2 l.2791-2796; §7.4 l.2850-2853 -->

**What the paper will not claim.** Nothing about prompts other than the one decode prompt and the one
2,048-token prefill prompt. Nothing about any machine, operating-system build, runtime or model beyond
those measured. Nothing about wall power or whole-machine energy, because the energy reported is that of
the processor alone. And no verdict of "no difference": a difference at or below the detection floor is
reported as not resolvable.
<!-- src: registration §1 l.885-894; claims_ladder.md l.46-48 -->

**When.** Nothing has been collected and nothing is scheduled: the design is sealed first. Once collection
starts, windows run back to back at any hour of the day or night, which comes to between two and four
windows in every 24 hours, not one a day. The three are expected to take 18 to 33 hours in all if each is
claim-usable at its first attempt. That total is the runs of the three windows (about 16 to 26 hours)
plus, for each window, its start check and the processing of its data that has to finish before the
next window can start (section 10).
<!-- src: registration §5.5 l.1903-1909 (18 to 23 h projected, 15.9 h of it runs; 28 to 33 h on the earlier probe's run times, 25.6 h of it runs).
     calc: 3 windows in 18 to 23 h is 3.1 to 4.0 per 24 h; in 28 to 33 h, 2.2 to 2.6 per 24 h -->

The sections that follow build each of these in order: what is measured (section 2), what one window does
(3), what can stop a window before it starts (4) and while it runs (5), what decides afterwards whether
its data may be used (6), what the paper will claim and the arithmetic behind each claim (7), what it will
not claim (8), the blinding (9), timing and status (10), and where a challenge would help most (11).

## 2. What is measured

### 2.1 The machine, the sampler and the boundary

The machine is one Apple laptop with an M3 Max processor, running macOS build 25G83 on its 140 W mains
adapter. Everything below happens on that one machine. The models run under MLX, Apple's machine-learning
framework.
<!-- src: registration §0.2 l.267-268; §4.6 l.1450-1451 (mlx 0.31.2, mlx-lm 0.31.3) -->

The instrument is Apple's `powermetrics` tool, called the *sampler* below. It is asked for one *power
record* every 100 ms. It never samples faster than asked: in the *prompt-length probe* a record in fact
spanned 127 to 130 ms. (The prompt-length probe is a set of trial windows run on 2026-10-03 and
2026-10-04 to choose the length of the prefill prompt. No claim rests on it, and this brief quotes it
only for timings and counts that the design was sized from.) Each record states the average power, over
its own time span, of the *processor package*: the CPU, the GPU and the neural engine combined.
<!-- src: registration §0.2 l.270-273; §0.7 l.413 (dates of the probe) -->

That package is the *measurement boundary*: the part of the machine whose energy is counted. Every element
of the power path, from the wall to the package:

```
 wall socket --> [power adapter] --USB-C cable--> [inline meter] --> [laptop power input]
                                                                             |
                                                                             +--> processor package: CPU + GPU +
                                                                             |    neural engine. Read by the sampler.
                                                                             |    THE MEASUREMENT BOUNDARY
                                                                             |
                                                                             +--> rest of the machine
                                                                             |
                                                [battery] <--either way-->---+
```

- *arrows:* the direction in which power flows. The battery's link carries power either way: into the
  battery when it charges, out of it when it helps.
- *wall socket:* mains AC.
- *power adapter:* the 140 W charger. Its AC-to-DC conversion loss is measured by nothing in this design.
- *USB-C cable:* carries 28 V DC from the adapter to the laptop.
- *inline meter:* a USB-C power meter in that cable. It reads voltage and current 50 times a second and is
  used only as a cross-check (section 2.5).
- *laptop power input:* what enters the laptop from the adapter.
- *processor package:* the only part whose energy the sampler reports, and so the only part any claim is
  about.
- *rest of the machine:* memory, storage, fans and the display (asleep during measurement).
- *battery:* under a heavy load it can discharge to help the adapter while the adapter stays connected
  (section 6.4). Its current is read once a second from the laptop's power controller.

<!-- src: registration §5.8 l.2011-2033; §1 l.887-894 (boundary label "M3 Max / MLX / powermetrics SoC rails") -->

### 2.2 From power records to phase energy

*Rule.* A phase is the stretch of time between two instants of a request, each timestamped by the
measuring program: prefill runs from the start of the request to the first output token, and decode from
there to the last. Each power record contributes its power multiplied by the length of the overlap
between its own time span and the phase. A record wholly inside the phase counts in full, a record that
straddles an edge of the phase counts in proportion to its overlap, and a record outside counts zero.

*Worked example (synthetic).* A phase runs from t = 10.00 s to t = 10.25 s. Record 1 covers 9.90 to
10.03 s at 20 W: the overlap is 0.03 s, giving 0.60 J. Record 2 covers 10.03 to 10.16 s at 30 W: overlap
0.13 s, 3.90 J. Record 3 covers 10.16 to 10.29 s at 30 W: overlap 0.09 s, 2.70 J. Phase energy = 0.60 +
3.90 + 2.70 = 7.20 J.
<!-- src: registration §0.4 l.310-315 -->

Two properties follow, and both are stated as design facts.

- The energy is *gross*: no idle power is subtracted. It includes what the processor would have drawn
  anyway over that time.
- A phase must overlap at least 3 power records, or no energy is computed for it. A phase shorter than one
  record can overlap at most two, so it is below this instrument's resolution and is not reported.

<!-- src: registration §0.4 l.312, l.316 -->

### 2.3 The two workloads

- **Decode workload.** One fixed 42-token prompt. The model is forced to produce exactly 512 output tokens
  (it always picks the most likely token and is not allowed to stop early). The decode phase of this
  request is the measured decode. Prefill produces the first of the 512 tokens, so the decode phase covers
  the other 511 generation steps. The prefill of this request, 42 tokens, lasts a few tens of
  milliseconds, shorter than one power record. It is registered as expected to be unresolvable, and no
  value for it will be printed.
- **Prefill workload.** A prompt of exactly 2,048 tokens, followed by 512 output tokens. The prefill phase
  of this request is the measured prefill. The prompt-length probe chose 2,048 as the shortest of 512,
  1,024, 2,048 and 4,096 tokens at which the prefill of every small-model run in the probe overlapped at
  least 5 power records. Five is the minimum of 3 (section 2.2) plus a safety margin of 2, fixed before
  the probe so that runs in these windows are not lost to that minimum.

<!-- src: registration §0.5 l.323-334; configs/campaigns/g2a_prefill_probe_25g83/registration_block3.md l.27-30, l.335-336 (the margin of 2 and its purpose) -->

### 2.4 The limit that timing sets

Phase energy depends on where the two edges of a phase fall among the power records, and that placement is
known only to within a timing error. Two separate timing errors are controlled. They are different
quantities with different sizes.

1. **Clock alignment.** The sampler and the measuring program run on the same laptop, but they do not
   record time in the same way. Each power record carries the sampler's own wall-clock label, which names
   only a whole second, and its elapsed duration. Where inside that second a record ends is therefore not
   recorded and has to be inferred. The edges of a phase are timestamped by the measuring program
   directly, to a few microseconds. Placing records against edges needs the offset between the sampler's
   record times and the measuring program's timestamps. For every run that offset is bounded from the
   run's own records, and a run is kept only if the bound is at most 5 ms. Section 4.1 builds this bound,
   because the start check predicts it before any run starts.
2. **Edge timing.** Even with the clocks aligned, a change in load that the software commands at one
   instant may appear in the power records at a slightly different instant. A *timing calibration*
   measures how different. The GPU is driven through 59 on/off pulses at commanded times. For each pulse
   an estimator fits the power records as a flat baseline plus a rectangle whose start and end may be
   delayed from the commanded times, and returns the range of delays consistent with the records. The
   calibration's *result* is the largest absolute delay over all 59 pulses. One calibration is taken
   before each window and one after it. The pair is judged against an *acceptance rule* fixed in advance
   from 24 earlier calibrations on this operating-system build. It has two limits. The opening result may
   be at most 36.5 ms, the largest among those 24. And the two results may not differ by too much: the
   larger of their difference and 14.5 ms (the largest of those 24 results minus the smallest) must not
   exceed 15.5 ms. Because 14.5 ms is itself below 15.5 ms, a pair meets the second limit exactly when
   its two results differ by at most 15.5 ms.

<!-- src: registration §0.14 l.720-731 (l.729: 2 µs of stamp resolution and padding); §0.11 l.458-469 (l.466-469: pre screen 0.036462861644980 s, bracket screen 0.014531 s, limit 0.01550217418713139 s) -->

*What the two errors cost in joules.* A timing error moves energy from one phase to its neighbour: the
amount is the error multiplied by how much the power changes across the phase edge. For clock alignment
alone, at a processor power of 40 W, an error of 5 ms moves at most 0.005 s × 40 W = 0.2 J across one
edge. For both errors together, the project's standing estimate is about 1 J, called the *attribution
floor*. Its arithmetic, made in July 2026 on the previous operating-system build: a combined timing
uncertainty of about 31 ms, most of it edge timing, at a phase edge where the power changes by about 33 W,
gives 0.031 s × 33 W ≈ 1 J. The attribution floor is printed beside each reported energy and is not folded
into that energy's interval. Its exact value on the current build, and whether the July derivation carries
over at all, are open and must be fixed before the seal.
<!-- src: registration §0.14 l.722-724; §0.10 l.451-454; §14 Q5 l.3302-3303; docs/decision_log.md D-078 clause 11 l.4762-4772 -->

### 2.5 A cross-check outside the boundary: the whole-machine meter

*The problem.* Every claim is a processor-package energy. A reader will ask what share of the machine's
energy that is, and whether the package figure moves with the machine's energy from run to run. The
sampler cannot answer, because it sees only the package.

*Mechanism.* The inline meter of section 2.1 records the laptop's power input throughout each window. For
each run, over the request being measured, three numbers are computed:

- **ΔE_package:** the package energy above the run's own idle level;
- **ΔE_machine:** the energy entering the machine above the same idle level. It has two terms: the meter's
  energy, and the battery's discharge energy, which the meter cannot see because the battery sits behind
  it;
- **ρ = ΔE_package ÷ ΔE_machine:** the package's share of the machine's extra energy.

*Worked example (synthetic).* Before a run, the idle machine reads 9.0 W at the meter and 0 W from the
battery. The request lasts 20.0 s, with a meter average of 52.0 W and a battery average of 1.5 W.
Meter term: (52.0 − 9.0) W × 20 s = 860 J. Battery term: 1.5 W × 20 s = 30 J. ΔE_machine = 890 J. With
ΔE_package = 712 J, ρ = 712 ÷ 890 = 0.80. Leaving the battery term out would give 712 ÷ 860 = 0.83, an
overstatement of the package's share whenever the battery helps.
<!-- src: registration §5.8 l.2004-2007, l.2049-2056, l.2062-2067 -->

*What it is used for.* What is reported from it is fixed in advance: ρ for each model, as its median, its
range and its interquartile range, and every run for which ρ falls outside the physically possible band
0 < ρ ≤ 1. The meter never refuses a window, never removes a run and never enters a claimed number. Its
boundary is the laptop's DC input plus the battery term; the adapter's conversion loss is excluded, so it
is not wall power either. In a bench test on 2026-10-06 the laptop's own reading of its input power agreed
with the meter to about 1% (median ratio 0.992 over 120 s at idle).
<!-- src: analysis plan §8.2 l.586-600, l.608-611; registration §5.8 l.2032-2033, l.2069-2071, l.2091-2092 -->

## 3. What one window does

### 3.1 One run

A run (the repository's word is *member*) is one inference request executed in its own process. Its
steps, in order:
<!-- src: registration §0.3 l.277-302 -->

1. **Idle baseline.** The sampler records the idle machine for 576 power records, about 75 s.
2. **Quiet check** (*idle admission* in the repository). The baseline must show that the machine was
   quiet. Two tests. First, the machine is on mains power with its displays asleep, the screensaver off,
   Low Power Mode off and no *thermal pressure* (the operating system's signal that the machine is hot
   enough to slow the processor). Second, over at least 30 samples of CPU activity, the 95th percentile
   of the fraction of time the cores were busy is at most 0.5, and the 95th percentile of processor power
   is at most 1.0 W. A refused baseline is retried once, at once. A second refusal aborts the run, which
   then counts as lost.
3. **Warm-up.** One untimed generation of the same request, so that the measured request does not pay
   first-call costs.
4. **Measured request.** The request whose phase energies are computed.
5. **Cooldown,** before the next run. (The first run of a stage has none. A stage is a batch of runs
   launched together; section 3.3 lists them.) The idle machine's processor power is taken in readings of
   50 power records each, averaged. A reading is nominally 5 s long, because records are asked for 100 ms
   apart, and about 6.5 s long in practice, because a record in fact spans about 130 ms (section 2.1).
   The next run starts at the first reading that is at most twice the previous run's idle-baseline
   average, with no thermal pressure, or after 300 s at the latest. A run whose cooldown reached 300 s is
   removed afterwards, because the machine never showed that it had recovered.

<!-- src: registration §0.3 l.285-297; §0.13 l.709-716; §0.6 l.350-354 (l.351: 50 records requested, about 6.5 s of wall time; l.353-354: the first member of a stage has no cooldown); §6.3 l.2170-2171.
     calc: 50 x 0.127 s = 6.35 s and 50 x 0.130 s = 6.5 s -->

*Worked example of the cooldown (synthetic).* The previous run's idle baseline averaged 0.037 W, so the
limit is 0.074 W. The first reading averages 0.082 W: wait. The second averages 0.045 W with no thermal
pressure: the next run starts, about 13 s after the cooldown began (two readings of about 6.5 s).
<!-- src: registration §0.6 l.359-361 -->

### 3.2 Units: repeats and quads

Runs are grouped so that *drift* in the machine (a slow change in its readings over time, from heat for
example) does not pass for a difference between conditions.

- A **repeat** is one run measured on its own. In windows 1 and 2, ten are run in a row for each workload.
- A **quad** is four consecutive runs in the order A, B, B, A, where A and B are two conditions. *Why this
  order:* a steady drift cancels inside a quad. *Worked example.* Suppose every run reads δ more than the
  run before it. The four positions then carry 0, δ, 2δ and 3δ of drift. Condition A (first and fourth)
  averages 1.5δ, and condition B (second and third) averages 1.5δ, so the A-versus-B difference gains
  nothing. A drift that curves does not cancel: with drift 0, 1, 4, 9 at the four positions, A averages
  4.5 and B averages 2.5.
- In windows 1 and 2, A and B are the *same* model and workload. Such a quad is a **null quad**: any
  A-versus-B difference in it can only come from the instrument and the machine. The detection floor is
  estimated from these.
- In window 3, A is Qwen3-1.7B and B is Qwen3-8B on the same workload. The quad's difference is
  d = (B1 + B2)/2 − (A1 + A2)/2.
- A **unit** is what the statistics treat as one independent draw: each repeat is one unit and each quad
  is one unit. So there are two kinds of unit, repeats and quads.

<!-- src: registration §0.8 l.418-434 -->

Each energy reported for one model and one phase (windows 1 and 2) rests on 20 planned units: 10 repeats
and 10 null quads, which is 50 runs. Each comparison (window 3) rests on 10 planned quads, 40 runs. So
windows 1 and 2 each hold 100 runs of the model under study, and window 3 holds 80.
<!-- src: registration §0.9 l.438-443; sizing_b5.json packs.*.science_members (100, 100, 80) -->

One limit, stated as a design fact: consecutive units share slow drifts (temperature, background load),
so treating them as independent draws is a modelling assumption, not a measured fact. Every reported
interval carries that caveat.
<!-- src: registration §0.8 l.432-434 -->

### 3.3 The order of a window

```
 windows 1 and 2:
 [start check] [C1] [Ref x12] [S S S] [decode: 10 repeats, 10 quads] [M] [prefill: 10 repeats, 10 quads] [E E E] [C2]

 window 3:
 [start check] [C1] [Ref x12] [S S S] [decode: 5 quads][i][5 quads] [M] [prefill: 5 quads][i][5 quads] [E E E] [C2]

 time runs from left to right
```

Every element of the diagram:

- **start check:** the physical checks of section 4. No model runs. It takes 4 to 47 minutes.
- **C1 and C2:** the timing calibrations of section 2.4, one before the runs and one after.
- **Ref x12:** twelve *reference runs*, which are runs of one fixed workload that is not under study.
  These twelve measure how much the instrument scatters when nothing changes (section 3.4).
- **S S S, M and E E E:** three more reference runs at the start, one at the midpoint and three at the
  end, used to measure drift across the window (section 3.4).
- **decode** and **prefill:** the runs of the model or models under study, on the decode workload and
  then on the prefill workload, grouped into the repeats and quads of section 3.2.
- **i** (window 3 only): one more reference run in the interior of each half. It is recorded as a
  diagnostic of drift inside that half and enters no test.

A *stage* is one group of runs launched together, and each window has ten. In windows 1 and 2 they are the
twelve, the start triplet, the midpoint, the end triplet and six stages of runs under study (each part
marked decode or prefill holds three: the ten repeats, then two stages of five quads). In window 3 they
are the same four reference stages, the two interior runs and four stages of five quads. Not drawn: the
machine sits idle for 60 s, a *settle*, before C1 and before each stage, eleven settles in all.
<!-- src: registration §5.1 l.1536-1541; §0.6 l.342-344; §0.12 l.489-495, l.503-507; §4.1 l.1185-1186; the three plan trees' stage_graph (order and stage count) -->

The reference runs add 19 runs to windows 1 and 2 (12 + 3 + 1 + 3) and 21 to window 3 (the two interior
runs more), which gives the 119 and 101 of section 1.
<!-- src: sizing_b5.json packs.*.auxiliary_members (19, 19, 21), members (119, 119, 101) -->

### 3.4 The reference drift check

*The problem.* A window lasts hours, and the machine's state can drift over that time: heat carried from
one run to the next, background activity. The quad order cancels a steady drift inside one quad, but it
does not measure the drift. Looking for drift in the runs under study would mean reading their energies,
which the blinding forbids. So each window measures its own drift on a workload that is not under study.
(The repository labels this check NEG-8, a name from the project's list of negative controls.)

*Mechanism.*

1. A **reference run** is one run of a fixed reference workload on a third, small model (Qwen2.5-1.5B,
   a 1,024-token prompt, 256 output tokens).
2. **The twelve** reference runs at the start of the window measure the instrument's scatter. Let s be the
   sample standard deviation of their energies, n their count, t the 97.5th percentile of Student's t with
   n − 1 degrees of freedom, U_j the mean of the j largest of the energies and L_j the mean of the j
   smallest. For a start mean over n_s runs and an end mean over n_e runs, the **drift bound** is

       bound(n_s, n_e) = max( max(U_ns − L_ne, U_ne − L_ns),  t × s × √(1/n_s + 1/n_e) ).

   The first term is the widest gap that a start mean and an end mean could show if both were drawn from
   the twelve themselves. The second is the 95% repeatability bound for the difference of two such means
   when nothing drifts.
3. **The screen.** The window passes when |mean of the end reference runs − mean of the start reference
   runs| ≤ bound. A window that fails is removed from the claims. The screen is applied twice, to the
   reference runs' gross energies and to the same energies with idle power subtracted, and both must pass.
4. **The drift allowance.** Take three values: the start mean, the midpoint reference run's energy and the
   end mean. Their *spread* is the largest minus the smallest. The window's drift allowance is
   max(spread, bound). It is charged as an uncertainty to each reported energy and each comparison from
   the window: each run carries half of it, so a difference of two conditions carries it once.
5. **Lost reference runs.** A reference run is *lost* when it failed, when its record cannot be read or
   validated, or when one of the measured physical conditions of section 6.2 occurred during it (a
   competing process during its request, for example). It is never lost because of its energy: the test
   that decides a loss does not read the energy. When the start triplet, the midpoint or the end triplet
   ends with fewer successful runs than planned, it gets one retry, during the window, from spare runs
   registered in advance: three for each triplet and one for the midpoint. A loss that is found only
   afterwards gets no retry. The screen then runs on the reference runs that survive. It needs at least
   two at the start and two at the end, and it uses bound(n_s, n_e) at the counts that survived, which
   is wider when fewer survive. The twelve may lose up to two in the same way: at least 10 must remain.
6. **A lost midpoint.** The midpoint is the only reference run inside the window, so without it a drift
   that rose in the middle and came back by the end goes unmeasured. Windows 1 and 2 keep their numbers
   and report the loss. Window 3 is then not claim-usable and is run again, because window 3 exists for
   its two comparisons.

<!-- src: registration §0.12 l.489-498, l.511-534, l.535-545, l.601-611, l.615-616, l.627-635; §5.3 l.1641-1644; analysis plan §2.4 l.129-132 -->

*Why item 5 exists.* In the first version of this rule the screen accepted only the full set of
references, so one start reference run refused by the quiet check removed the whole window. And a
reference run measured during a competing process was kept, although its energy then described the
competing process and not the instrument.
<!-- src: registration preamble l.157-164 -->

*Worked example (synthetic; recomputed for this brief).* The twelve energies are 99.62, 99.71, 99.80,
99.88, 99.93, 99.97, 100.04, 100.09, 100.15, 100.22, 100.31 and 100.38 J. Then s = 0.2353 J, t = 2.201,
U_3 = 100.3033 J, L_3 = 99.7100 J, U_2 = 100.3450 J and L_2 = 99.6650 J.

- With every reference run present, the counts are (3, 3) and the bound is max(100.3033 − 99.7100,
  2.201 × 0.2353 × √(2/3)) = max(0.5933, 0.4228) = 0.5933 J.
- Now suppose the start triplet reads 100.02 J, then a run refused by the quiet check, then 99.91 J. One
  spare is run and reads 99.95 J. Start mean over three runs: 99.96 J. The midpoint reads 100.20 J.
- The end triplet reads 100.26, 100.19 and 101.08 J, and the recorded physical conditions show a
  competing process during the third. That run is lost, with no retry, because the loss is found only
  after the window. End mean over two runs: 100.225 J.
- The counts are now (3, 2). The bound is max( max(100.3033 − 99.6650, 100.3450 − 99.7100),
  2.201 × 0.2353 × √(1/3 + 1/2) ) = max( max(0.6383, 0.6350), 0.4727 ) = 0.6383 J.
- Screen: |100.225 − 99.960| = 0.265 J ≤ 0.6383 J. The window passes.
- Allowance: the spread of 99.96, 100.20 and 100.225 is 0.265 J, so the allowance is max(0.265, 0.6383)
  = 0.6383 J, and each run carries 0.3192 J.

Had the contaminated end run been kept, the end mean would be 100.51 J and the screen statistic 0.55 J,
close to failing the 0.5933 J bound because of a competing process and not because of drift.
<!-- src: registration §0.12 l.670-685; calc: scratch recompute with the repository's t table -->

## 4. What can stop a window before it starts

*The rule.* A window is refused before it starts only for a *physical hazard*: a condition of the machine
that would corrupt a measured energy if collection ran through it. And it is refused only when that
condition is **measured directly**. A check that reads a stand-in for the condition (a settings string, a
record that some step was performed, the wording of a command's output) is not allowed to refuse. This
rule replaced an earlier design in which a series of record-keeping checks had to verify before a window
could start, and in which one failed run discarded the whole window.
<!-- src: registration preamble l.27-36; §0.15 l.750-757 -->

The *start check* (the *arm* in the repository) runs inside a scheduled job, with no person and no AI
agent present. It takes instant readings of battery, heat, disk and clock rate, tests the sampler for
about 40 s, and then holds a *dwell* of 180 to 2,700 s during which competing processes and the
steadiness of the clock are measured. The runs therefore begin 4 to 47 minutes after the scheduled start.
A refusal ends the attempt with nothing launched.
<!-- src: registration §4.1 l.1172-1187 -->

### 4.1 The six physical hazards

| Hazard | Why it would corrupt an energy | What is measured | The window is refused when | Example |
|---|---|---|---|---|
| Clock | A jump of the wall clock, or a wall clock running too fast or slow against the hardware counter, breaks the 5 ms clock alignment of section 2.4 | The wall clock minus a hardware counter that nothing adjusts, once a second; and f, the kernel's stored rate correction for the wall clock, in parts per million (ppm) | The predicted worst-case alignment bound exceeds 5 ms; or, during the dwell, the wall clock minus the hardware counter moves more than 1 ms away from the straight line that the rate f predicts from its value at the start of the dwell; or f changes during the check | Worked below |
| Battery | While the battery charges it heats, and the machine draws more from the adapter than the work needs; off the adapter the machine runs under a different power policy | Adapter connected (yes or no), charging (yes or no), and the battery current in mA, signed | The adapter is not connected; or the battery is charging; or the current exceeds 200 mA in either direction on the idle machine | Synthetic: idle with 0 mA passes; idle with +450 mA (charging) refuses, and the window is tried again when charging ends |
| Heat | Under thermal pressure the processor is slowed, which changes both power and duration | The operating system's thermal-pressure level, where 0 means none | The level is not 0 | Synthetic: level 1 refuses |
| Competing process | Another process's CPU work during a request adds energy that would be counted as the model's | CPU-seconds used per second by every process outside the measurement, from the growth of each process's cumulative CPU time between two snapshots | No stretch of 180 s is found, within 2,700 s, in which every outside process stays at or below 0.05 CPU-seconds per second (5% of one core) | Worked below |
| Disk | A failed write in the middle of a window loses data | Free bytes on every volume the window writes to | Free space is below the window's planned bytes, times the copies kept on that volume, plus 20 GiB | Registered sizes: window 1 plans 22.4 GiB (at most 126 runs, spares included, at 182 MiB each) and three copies land on one volume, so 3 × 22.4 + 20 = 87.2 GiB is required; 264 GiB was free on 2026-10-05, which passes |
| Sampler | A sampler running slower than asked leaves phases with too few power records | A 300-record recording of the idle machine, taken through the same path the runs use | It does not return exactly 300 records within 55 s; or the median record interval exceeds 150 ms; or the largest exceeds 200 ms | On 2026-09-19 the sampler delivered a record every 244 to 250 ms in this scheduled-job setting; 300 such records take 73 to 75 s, which refuses |

<!-- src: registration §4.2: clock l.1197-1206 (l.1204 with §0.14 l.738-739: the 1 ms test is on the wall clock minus the hardware counter, less f x elapsed time); battery l.1232-1237, l.1269-1272; thermal l.1277-1282; contention l.1284-1293;
     disk l.1308-1319; instrument l.1322-1325; thresholds §4.3 l.1336-1347.
     calc: 300 x 0.244 s = 73.2 s and 300 x 0.250 s = 75.0 s; +450 mA and level 1 are synthetic inputs chosen for this brief -->

Among these six hazards, a measurement that cannot be taken is not a refusal, with one exception. If the
battery reading times out, for example, the start check records "unmeasured" as a flag and goes on,
because the same quantity is measured throughout the window anyway. The exception is the sampler: a
sampler that cannot be tested is itself the hazard.
<!-- src: registration §0.15 l.760-765; §4.1 l.1187-1190; §4.5 l.1418 (an unreadable process list refuses at the start check, which is why the sentence is limited to the six hazards) -->

**The clock hazard, built and worked.** For one run, the clock-alignment bound of section 2.4 is computed
from the run's own records, in three steps.

1. Assume that over the run the wall clock runs at one steady rate against the hardware counter, with no
   jump.
2. The end of every power record, found by adding up the records' elapsed durations, must fall inside the
   whole second that the record's label names (widened by 250 µs). Find every pair of clock offset and
   clock rate that satisfies all the records at once. At the first record, those pairs allow a range of
   offsets; half the width of that range is the run's **offset half-range**.
3. The run's bound is the offset half-range, plus the amount the wall clock moved against the hardware
   counter during the run, plus 2 µs. The run is kept when it holds at least 60 s of records and the
   bound is at most 5 ms.

<!-- src: registration §0.14 l.725-731 -->

The start check predicts this bound for the worst run before any run starts. That prediction is the
*frequency gate*:

    3.7 ms + (|f| + 0.25 ppm) × 335 s ≤ 5 ms.

Here 3.7 ms is the largest offset half-range any run showed in the prompt-length probe (3.6 ms) plus a
margin of 0.1 ms. 335 s is the longest stretch of sampling that any run in these windows can have (a
Qwen3-8B run that needs both tries of the quiet check). 0.25 ppm allows for the clock's rate during a run
differing from the stored f.

*Worked example (registered).* On 2026-10-05, f was −3.17 ppm. One ppm over 335 s is 0.335 ms, so the
predicted bound is 3.7 + (3.17 + 0.25) × 0.335 = 4.846 ms, at most 5 ms: pass. At |f| = 3.7 ppm it would
be 3.7 + 3.95 × 0.335 = 5.023 ms: refuse. The gate passes for |f| up to 3.63 ppm.
<!-- src: registration §4.2 l.1199-1204; §0.14 l.734-746 -->

Why the clock is steady at all: at every start check the laptop's automatic network time is switched off,
as an action, because with it off nothing sets the clock and the clock only drifts at the steady rate f.
What the setting then reports is recorded, and nothing depends on it. Whether the clock is in fact
undisturbed is what the dwell measures.
<!-- src: registration §4.4 l.1361-1364; §0.14 l.736-737 -->

A check that always passes looks the same as a quiet clock. So at the end of the first window that runs,
after every recording is finished, the system turns network time back on deliberately and confirms that
the clock check sees the resulting correction: a *positive control*. With network time off the clock was
about 1.15 s away from a time server on 2026-10-05, so the correction should be far above the 5 ms the
control needs to see. Its result is reported and touches no measured number.
<!-- src: registration §3 l.1119-1140 -->

**The competing-process hazard, worked.** *Registered example:* a process whose cumulative CPU time goes
from 12.40 s to 13.10 s across a 10 s interval used (13.10 − 12.40) ÷ 10 = 0.07 CPU-seconds per second,
above the 0.05 limit. At the start check the dwell is cut into 30 s intervals, an interval is clean when
no outside process exceeds the limit, and the window may start after six consecutive clean intervals
(180 s). *Synthetic example:* a background indexer that stays above the limit for the first 240 s delays
the start to 240 + 180 = 420 s. One that never stops refuses the window at 2,700 s. This hazard is not
hypothetical: on 2026-09-22 a background indexing process contaminated measurements this way.
<!-- src: registration §4.2 l.1284-1293 -->

### 4.2 Refusals outside the six hazards

- **An AI coding-agent process is running.** The project's code is written and reviewed by AI agent
  sessions (a session is one running instance of an AI model) on this same laptop, and their work would
  compete with a measurement. Two agent programs are used on it, Claude Code and Codex. The start check
  first lists every process whose command line contains either program's name. That list is too wide on
  purpose (a file path can contain a name), so each listed process is then judged by the program it is
  in fact running: it is an agent when its executable is one of the two programs, or when it is a
  JavaScript runtime whose command line names one of their packages. The window's own processes are
  ignored, and a listed process that cannot be judged counts as an agent. The start check refuses if any
  agent remains, or if the list cannot be read. The same check runs again just before the runs begin and
  every 30 s during the window.
- **An operating-system build the timing calibration never covered.** Every timing bound in a window
  rests on the acceptance rule of section 2.4, which was derived on one macOS build. After an
  operating-system update the sampler and the scheduler may behave differently, and that rule says nothing
  about them. The start check reads the build and refuses, in about a minute, if it is not the calibrated
  one.
- **The launch itself.** When the start check has passed, and just before the runs are launched, the
  system writes into the window's storage a small record that ties every run's data to this window, its
  plan and its timing calibrations, and reads the record back in the way each run will. Two findings at
  that step refuse the window. First, the machine has restarted since the record was written: runs are
  timestamped on counters that begin again when the machine restarts (the hardware counter of section
  4.1 is one), so timestamps from before and after a restart cannot be placed on one time axis. Second,
  the record cannot be written, after one retry 5 s later, because the plan's sealed list of the
  configuration files its runs may use cannot be read: no run's configuration could then be checked
  against that list, and every run would refuse itself. Any other fault at this step is recorded as a
  flag, and the runs are launched.

<!-- src: registration §4.5 l.1370-1373, l.1379-1404 (the matcher), l.1416-1420; §4.7 l.1513-1530; §0.17 l.805-823 (launch record and its two refusals); joulewise/b5/driver.py l.88, l.93 (the two refusal codes), l.142 (5 s retry) -->

The project owner is notified before each start and can veto it.
<!-- src: registration §7.2 l.2831 -->

## 5. What can stop a window while it runs

*The rule.* A failed run costs only itself. In the earlier design one aborted run ended the window. With
119 runs, and 1 run in 37 refused by the quiet check (the rate measured over the prompt-length probe and
an earlier, incomplete attempt at it), a window with no lost run would have had a chance of
(36/37)^119 ≈ 0.04.
<!-- src: registration §0.13 l.715-716; §5.3 l.1646-1647; §6.6 l.2484-2487 -->

*The monitor.* From the moment the start check passes until the window's processes are gone, a background
program, the **monitor**, records the hazard quantities: the wall clock minus the hardware counter every
1 s and f every 5 s; adapter and charging state and the heat level every 5 s; battery current every 1 s;
per-process CPU every 10 s; free disk every 60 s. Every reading carries timestamps on the machine's
clocks, so that afterwards it can be matched to the time span of each run. The monitor's own CPU work is
inside the measurement boundary. It is disclosed with each window and is not subtracted.
<!-- src: registration §0.17 l.824-832; analysis plan §8.1 l.508-511 -->

A window in progress is stopped only by these:

- before the first run: the window's entry in the append-only log of calibrations cannot be opened; the
  opening calibration cannot be recorded; or the opening result exceeds the 36.5 ms limit of the
  acceptance rule (section 2.4);
- at any time: free disk falls below 10 GiB; an agent process appears; the monitor has written no battery
  or competing-process reading for about 10 minutes; or the window's deadline passes (section 10).

<!-- src: registration §5.1 l.1543-1549; §0.11 l.467, l.475-477; §4.2 l.1320 -->

Everything else is recorded and the window goes on. Three rules keep a bad stretch from costing the
window:

- A run has a time limit of 1,800 s, about 2.6 times the longest a run is planned to take with every wait
  at its limit (696 s). A run that reaches the limit is killed and counted as lost. After two such runs
  in a row the window skips ahead to its end reference runs and its closing calibration.
- If fewer than 10 of the twelve reference runs succeeded, that stage is run once more to measure the
  ones that never produced a record. A run that was measured and failed is never measured again.
- The start triplet, the midpoint and the end triplet each have their one retry from spares (section
  3.4).

<!-- src: registration §5.2 l.1620-1629; §5.1 l.1592-1606 -->

## 6. What decides afterwards whether the data may be used

### 6.1 Flags and the catalog

After a window's processes have exited, a program (the *harvest* in the repository) works from an archive
copy of the window. It recomputes, from the preserved raw bytes, every check that protects a number,
matches the monitor's readings to each run's time span, and writes the flags.

A **flag** is one recorded fact: a code naming what happened, its scope (the window, a stage, a quad or
one run), its time interval, the observed and expected values, and the path and hash of the raw evidence.
A flag never stops collection. The **flag catalog** assigns each code exactly one effect. At this draft it
lists 192 codes: 40 remove the run they name, 32 remove the whole window, and 120 are reported and remove
nothing. The post-window program looks effects up; it never decides them.
<!-- src: registration §0.16 l.771-780; §0.17 l.838-840; flag_catalog.json effect counts (120 DISCLOSE, 40 EXCLUDE_MEMBER, 32 EXCLUDE_WINDOW) -->

*Which flags are allowed to remove anything.* Exactly two kinds. **Physics:** a physical hazard, measured
directly, would have corrupted the energy. **Number integrity:** a number would be wrong, or could not be
tied to what it claims to measure (which code, model or plan ran; the calibration; the drift screen; which
unit a run belongs to). Everything else, such as a missing record of a step, the format of a record or a
log that was not written, is reported and removes nothing. A test in the repository enforces this for
new code: every new place where the code that runs during a window refuses, stops or excludes must be
listed, classed as one of the two kinds and say what it protects, or the test fails. Refusal sites older
than the rule are held in a frozen list that can only shrink.
<!-- src: registration §6.11 l.2711-2715, l.2725-2731, l.2752-2761 -->

### 6.2 Examples of each effect

- **Removes one run:** the quiet check refused it twice; its clock-alignment bound exceeds 5 ms; a
  competing process exceeded 0.05 CPU-seconds per second during its measured request; the battery was
  charging, or the adapter was lost, during the run; thermal pressure during the run; the wall clock
  jumped during the run; its observed token counts differ from the registered ones; its cooldown reached
  300 s; it hit the 1,800 s limit.
- **Removes the window:** the code, the model or the plan that ran differs from what was sealed; a timing
  calibration is missing, or the pair fails the acceptance rule; the drift screen failed or its bound
  could not be derived; a number to be reported is left with fewer than 8 units of either kind.
- **Reported only:** the battery helping the adapter (section 6.4); a lost reference run that the rule of
  section 3.4 absorbed; failures of record keeping, with the three registered exceptions given next; the
  meter's own quality flags; the result of the clock positive control.

The three exceptions are the record-keeping failures that could hide a removal or change a number. Two
concern a flag whose stored record is damaged, cut off in the middle of being written, for example. Such
a record is read for what it still shows of its code. If it could have been a window-removing flag, the
window is removed. Failing that, if it could have been a run-removing flag and it still names its run,
that run is removed. Otherwise the damage is reported only. The third: if the files the post-window
program reads change while it is reading them, the window is removed.

<!-- src: registration §6.3 l.2155-2171, l.2214; §6.4 l.2264-2268, l.2344-2354; §6.5 l.2361-2441; §6.2 l.2140-2151 (RECORDS row l.2150: three exceptions), l.2124-2130 (the damaged-line rule); §6.5 l.2442-2445 (source bytes changed during the harvest) -->

### 6.3 The 8-of-10 rule

*Rule.* A removed repeat removes that one unit. A removed run inside a quad removes the whole quad, so
that the A, B, B, A cancellation is never broken. A window is **claim-usable** when no window-removing flag
fired and every number to be reported keeps at least 8 of its 10 units of each kind: 8 repeats and 8 quads
for a reported energy or a floor, 8 quads for a comparison.
<!-- src: registration §6.6 l.2473-2478; §0.16 l.792-793 -->

*Worked example (synthetic).* In window 1, take the decode energy: 10 repeats and 10 quads planned. A
competing process is measured during repeat 6, which is removed: 9 repeats remain. In quad 5 one run is
refused twice by the quiet check, and in quad 9 one run's cooldown reaches 300 s: both quads are removed
whole, and 8 quads remain. 9 ≥ 8 and 8 ≥ 8, so the number stands. It is computed over the kept units
(section 7.1 computes exactly this case), and the removals are printed beside it. Had a third quad lost a
run, 7 quads would remain, the window would not be claim-usable, and it would be run again.

*Why 8.* With 8 units of each kind in place of 10, the interval's half-width (half the distance between
its two ends; section 7.1 gives its formula) grows by at most (2.365 ÷ 2.262) × √(10/8) − 1 ≈ 17%. And
if each run is refused by the quiet check independently at the measured rate of 1 in 37, a window keeps
both of its reported energies at or above the minimum with probability about 0.85, against 0.04 under
the old all-or-nothing rule.
<!-- src: registration §6.6 l.2482-2487; calc: P(at most 2 of 10 repeats lost at 1/37) x P(at most 2 of 10 quads lost at 1-(36/37)^4), squared for two numbers = 0.849 -->

*Running a window again.* A window that is not claim-usable is run again as a new *attempt*, with fresh
storage and fresh calibrations, until one attempt is claim-usable. Then the next window in the fixed
order starts. Each window's analysed data come from its first claim-usable attempt only: nothing is
pooled, topped up or replaced across attempts.
<!-- src: registration §7.2 l.2791-2796 -->

*What that selection can and cannot see.* The decision to run again reads only the claim-usable verdict.
That verdict reads no energy of a run under study, with one registered exception: a run is removed when
the energy that its clock-alignment uncertainty could move is more than a quarter of the run's own phase
energy. Only the pass or fail of that test is used, and during collection such a run is reported as
"removed", without the reason. The verdict does read reference-run energies (the drift screen), idle
power (the quiet check), timing and the hazards. So running again cannot select on the outcome, but every
reported number is conditional on a window that passed these quiet, timing and drift checks. The paper
prints, beside every number, how many attempts its window took and why each earlier one was not used.
<!-- src: registration §7.6 l.2877-2881; §6.3 l.2166-2168; §8 l.2891-2892; joulewise/reduce.py l.2349-2361 (ratio limit one quarter) -->

*What stops repetition.* If two attempts in a row of the same window fail for the same class of cause,
the next step is a design review, not a third attempt. If, across every attempt so far, at least 5 runs
have a recorded clock-alignment result and more than half of them fail it, the timing instrument is
failing, and all collection stops. If a defect is found in code that runs during a window, and an
already finished window executed that code, the finished windows are kept but never analysed, and
collection restarts at window 1, because window 3 is judged against floors from windows 1 and 2 and all
three must have run the same code.
<!-- src: registration §7.3 l.2835-2839; §7.4 l.2850-2853; §7.5 l.2859-2868 -->

### 6.4 A ruling you may want to challenge: battery help is reported, not excluded

*The problem.* On its 140 W adapter, this laptop sometimes draws from the battery as well when the load
is heavy, with the adapter still connected and the battery not charging. In a bench test on 2026-10-06
under a deliberately heavy load (a CPU-burning job plus Qwen3-8B generations) the battery current was
nonzero in 126 of 170 s and reached −5,331 mA, negative meaning discharge. Until that day the rule removed
any run during which the battery discharged by more than 200 mA.
<!-- src: registration §9.2 l.2992-2995; §4.2 l.1259-1262 -->

*The ruling.* Discharge with the adapter connected is now reported for each run and does not remove it.
A run counts as *helped* when any of the once-a-second battery-current readings during its measured
request is negative. *Worked example (synthetic):* a request lasts 5 s and the readings are −865, −1,200,
−400, −150 and 0 mA, with the adapter connected and the battery not charging. The run is kept and marked
as helped; the −150 mA reading alone would have marked it. Had one reading been +450 mA, which is
charging, the run would have been removed.

*Its four reasons.*

1. The processor package is fed through regulators downstream of both sources, so the package energy the
   sampler reports is the same whether the adapter or the battery delivered it.
2. Removing the helped runs would bias the result. Help happens when the load is highest, so removal
   would select runs by load and pull the kept averages down, most of all for the large model.
3. The evidence on hand shows no slowdown: in that day's measurements Qwen3-8B decoded at 69.1 to 72.6
   tokens per second while the battery helped, against 68.9 to 71.1 without help.
4. The two hazards behind the original rule stay covered. Charging, and loss of the adapter, still remove
   the run, and the start check still refuses any battery current on the idle machine. And the meter's
   blind spot is closed by adding the battery term to the whole-machine energy (section 2.5).

<!-- src: registration §9.2 l.3002-3010; §6.4 l.2258-2268, l.2329-2338 (definition of help and the synthetic readings) -->

*What the reader gets.* Every reported energy and each comparison is printed twice: over all kept units,
and again without the units that hold a helped run. The first is the reported value. Neither is chosen
after the fact.
<!-- src: registration §9.2 l.3012-3014; analysis plan §8.1 l.483-496, l.500-503 -->

*What would reopen it.* Power-mode changes that reproducibly accompany battery help; lower package power
or fewer tokens per second in helped seconds than in matched seconds without help; or a rise in battery
temperature concentrated where the help occurs.
<!-- src: registration §9.2 l.3021-3023 -->

A related risk is conceded in the same way. Removing runs for heat or for a competing process could also
bias an average, if those conditions go with heavier load. The analysis plan proposes a labelled
*sensitivity line* for it: the same number recomputed with those removals not applied, printed beside the
primary value and never in place of it. The seal review decides whether to adopt that line.
<!-- src: analysis plan §8.1 l.475-482; registration §14 Q6 l.3304-3307 -->

## 7. What the paper will claim, and the arithmetic of each claim

Each rule below was fixed before any data existed. The worked examples are synthetic.

### 7.1 Reported phase energy (rung L1)

Four numbers: for each of the two models, the decode energy and the prefill energy at 2,048 prompt
tokens, each from that model's own window.

*Arithmetic.* Let r be the phase energies of the n_r kept repeats, and b the four-run averages of the n_b
kept quads.

- Mean: m = 0.2 × mean(r) + 0.8 × mean(b). The weights are fixed by the plan, in which 10 of the 50 runs
  are repeats and 40 are quad runs. With all 20 units kept, m equals the plain average of the 50 runs.
- Variance of m: V = 0.04 × s_r² ÷ n_r + 0.64 × s_b² ÷ n_b, where s_r and s_b are the sample standard
  deviations of r and of b.
- Half-width: h = t × √V, where t is the 97.5th percentile of Student's t with min(n_r, n_b) − 1 degrees
  of freedom.
- Timing term: every run records two amounts in joules. One is how far its phase energy can move when
  the power records shift within its clock-alignment bound. The other is its half share of the window's
  drift allowance (section 3.4). For each of the two, average it over the kept repeats and over the runs
  of the kept quads, and weight those two averages 0.2 and 0.8. The timing term is the sum of the two
  results. (A third registered amount, a bound on the error of interpolating between point samples at
  the two edges of a phase, is zero here, because each power record is already an average over its own
  stated span and nothing is interpolated.)
- Interval: from m − h − (timing term) to m + h + (timing term).

<!-- src: analysis plan §4 l.221-247 (l.233-236: the three recorded bounds; the interpolation bound is identically 0 for interval-support traces); joulewise/reduce.py l.541-555 -->

*Worked example (synthetic).* Repeats: 10.0, 10.2, 9.9, 10.1, 10.0, 10.3, 9.8, 10.1, 10.0 and 9.6 J
(mean 10.0, s_r = 0.2). Quad averages: 10.4, 10.1, 10.3, 10.2, 10.5, 10.0, 10.2, 10.3, 10.1 and 9.9 J
(mean 10.2, s_b = 0.1826). Then m = 0.2 × 10.0 + 0.8 × 10.2 = 10.16 J. V = 0.04 × 0.04 ÷ 10 + 0.64 ×
0.03333 ÷ 10 = 0.002293, so √V = 0.04789 and h = 2.262 × 0.04789 = 0.1083 J. With a timing term of
0.060 J the interval is 9.99 to 10.33 J.

*The same data with the removals of section 6.3* (repeat 6 and quads 5 and 9 removed, so n_r = 9 and
n_b = 8): m = 0.2 × 9.9667 + 0.8 × 10.175 = 10.133 J; t has 7 degrees of freedom, 2.365; h = 0.1152 J,
6.3% wider; with the same timing term of 0.060 J the interval is 9.96 to 10.31 J.
<!-- src: analysis plan §4 l.259-271; calc: scratch recompute -->

Each number is also printed per token: the decode energy divided by the 512 output tokens that the
runtime reports, and the prefill energy divided by the 2,048 prompt tokens. Dividing by all 512 is the
registered convention, although the first of them is produced in prefill and the decode phase produces
the other 511; the printed label says so. Beside each number stand its kept units, its removals with
their causes, the number of attempts its window took, and the attribution floor of section 2.4.
<!-- src: analysis plan §4 l.248-257 (l.249-251: T is the runtime-observed output token count, 512, of which the decode phase produced the last 511, and the printed name); registration §0.5 l.326-327; analysis plan §8.1 l.466-474 -->

*What the interval covers.* Variation from repeat to repeat and from quad to quad inside one window, plus
the recorded timing term. It does not cover variation between windows or between days. The analysis plan
registers one check of that: the same model's energy is also estimated from window 3's quads, and if the
two estimates differ by more than their intervals cover, the paper says so in a fixed sentence.
<!-- src: analysis plan §4 l.278-280; §8.1 l.512-520 -->

### 7.2 Detection floors

*What a floor is, physically.* In a null quad both conditions are the identical workload, so any
difference between them was produced by the instrument and the machine. The floor is the largest such
false difference that the registered estimator allows, and hence the smallest real difference the
instrument can resolve. Each model and phase gets a floor in two forms: one from the ten repeats (how far
single runs scatter around their mean) and one from the ten null quads (how large a false A-versus-B
difference can be). The null-quad form is built first. The repeat form is then stated as two changes to
it.

*Arithmetic (null-quad form).* Let d_1 … d_n be the differences of the n kept null quads, each
(B1 + B2)/2 − (A1 + A2)/2, with mean d̄ and sample standard deviation s.

- Statistical floor: the larger of max |d_k| and |d̄| + t × s × √(1 + 1/n), where t is the 97.5th
  percentile of Student's t with n − 1 degrees of freedom. The second expression bounds, at 95%, where
  one more null difference would fall.
- Timing-widened floor: each d_k is known only to within ± w_k joules. w_k is how far the quad's
  difference can move when its phase edges shift within the timing-calibration result of section 2.4,
  plus half the sum of its four runs' own clock-alignment amounts (for each run, how far its phase
  energy can move when its power records shift within that run's clock-alignment bound). The statistical
  floor is recomputed with every d_k moved to one end or the other of its range, in all 2^n
  combinations, and the largest result is taken.
- The floor used is the larger of the two. With fewer than 10 kept units it is multiplied by a guard: a
  safety factor for small samples, fixed in advance and applied on top of the growth of t and of
  √(1 + 1/n) as n falls. The guard is √(9 ÷ (n − 1)): 1.061 at n = 9 and 1.134 at n = 8.

<!-- src: analysis plan §5 l.284-317 (l.315: the local width is half the sum of the four members' own residual half-widths; l.303-304: the guard);
     joulewise/detection_floor.py l.846-854 ("frozen, accepted operational safety factor"); joulewise/dominance_closeout.py l.616 -->

*Worked example, null-quad form (synthetic).* d = 0.10, −0.05, 0.20, 0.00, −0.10, 0.05, 0.15, −0.05, 0.10
and 0.00 J. Then d̄ = 0.04 J, s = 0.0966 J and max |d_k| = 0.20 J. Statistical floor: max(0.20, 0.04 +
2.262 × 0.0966 × √1.1) = max(0.20, 0.2692) = 0.2692 J. With w_k = 0.30 J for every quad, the largest of
the 1,024 recomputed values is 1.0349 J. It occurs when each d_k is pushed away from zero (the two zeros
upward), to 0.40, −0.35, 0.50, 0.30, −0.40, 0.35, 0.45, −0.35, 0.40 and 0.30 J. The floor is 1.0349 J.
<!-- src: analysis plan §5 l.324-326; calc: repository function comparative_false_effect_floor and a brute-force check -->

*Arithmetic (repeat form).* The same three steps over the n kept repeats, with two changes.

- In place of the d_k, take each kept repeat's phase energy minus the mean of the kept repeats. These
  deviations average zero, so the |d̄| term is absent: the statistical floor is the larger of the largest
  |deviation| and t × s × √(1 + 1/n), where s is the sample standard deviation of the kept repeats'
  energies.
- A repeat's timing width w is how far that run's phase energy can move when its power records shift
  within the run's own clock-alignment bound (the first of the two per-run amounts of section 7.1). For
  the timing-widened floor, each repeat's energy is moved to one end or the other of its range, the mean
  and the deviations are recomputed from the moved energies, and the statistical floor is taken again,
  in all 2^n combinations.

<!-- src: analysis plan §5 l.297-304 (deviations, prediction, point floor, guard), l.309 (w_i for this form); joulewise/detection_floor.py l.1099-1128 -->

*Worked example, repeat form (synthetic; the analysis plan's own).* The ten repeat energies of section
7.1 have mean 10.0 J and s = 0.2 J, and the largest |deviation| is 0.4 J (the 9.6 J repeat). Statistical
floor: max(0.4, 2.262 × 0.2 × √1.1) = max(0.4, 0.4745) = 0.4745 J. With w = 0.05 J for every repeat, the
largest of the 1,024 recomputed values is 0.5730 J. It occurs, for example, when the ten energies are
moved to 9.95, 10.25, 9.85, 10.15, 9.95, 10.35, 9.75, 10.15, 10.05 and 9.55 J: each repeat away from the
mean, and the three that sit on the mean split two down and one up. The floor is 0.5730 J.
<!-- src: analysis plan §5 l.320-321; calc: repository function absolute_false_effect_floor and a brute-force check over the 1,024 corners (reviser, 2026-10-07) -->

### 7.3 Whether timing is what limits the instrument

*The question.* Is timing uncertainty the part of the floor that limits the measurement? For each model,
phase and form of floor, the ratio

    R = timing-widened floor ÷ statistical floor

answers it. R ≥ 2 means that letting each value move within its timing uncertainty at least doubles the
floor. In the null-quad example above, R = 1.0349 ÷ 0.2692 = 3.84. In the repeat-form example,
R = 0.5730 ÷ 0.4745 = 1.21, which is below 2.

There are eight such ratios (two models, two phases, two forms). There are four more, for the null-quad
form only (two models by two phases), of a variant in which the timing shift has one shared sign across
all quads. If every one of them is at least 2, the paper may describe the instrument in its subtitle as
"attribution-limited", meaning limited by where energy is assigned in time and not by scatter. If any is
below 2, each one that fell short is reported plainly and the subtitle is not used. Each ratio is printed
with its numerator and denominator in joules and is labelled as a point value with no interval.
<!-- src: analysis plan §6 l.341-360 (l.347: the two example ratios, 1.21 and 3.84; l.352: the four shared-sign ratios are comparative only); registration §1 l.872-875 -->

### 7.4 The two comparisons (rung L2, if earned)

Window 3 yields two comparisons, Qwen3-8B minus Qwen3-1.7B: one for decode energy and one for prefill
energy at 2,048 tokens. Both are registered as two-sided tests on which the claims rest, with the
expected direction stated in advance (the larger model uses more). The order inside every quad is fixed,
not randomized: small model, large, large, small.
<!-- src: analysis plan §7.1 l.375-378 -->

*Arithmetic,* over the n kept quads (at least 8):

1. For each quad, d_k = (B1 + B2)/2 − (A1 + A2)/2, with A the small model and B the large one.
2. d̄ is the mean of the d_k, s_d their sample standard deviation, and se_rep = s_d ÷ √n.
3. A run's summary can also carry variances, in joules squared, of random errors that are estimated
   inside that one run. For each such error term, one quad's variance is (var_A1 + var_A2)/4 +
   (var_B1 + var_B2)/4. Summed over the kept quads and divided by n², this is that term's squared
   standard error, and se_met² is the sum over the terms. Then se = √(se_rep² + se_met²). The one term
   the analysis code reads today is the variance of a run's idle-power average, and it reads that term
   only for an energy from which idle power has been subtracted. The phase energies compared here are
   gross, so as the code stands the list of terms is empty for both comparisons, se_met is 0 and
   se = se_rep. Where a term is present, that run-level random error is counted twice, once inside s_d
   and once in se_met; the interval is then wider than 95% coverage needs, and the paper says so.
4. First interval: d̄ ± t × se, with t the 97.5th percentile of Student's t with n − 1 degrees of freedom.
5. Second interval: the first, widened on both sides by D. D collects the two per-run timing amounts of
   section 7.1: for each of the two and each quad, the average over the two A runs plus the average over
   the two B runs; then the mean over the kept quads; then the sum of the two.
6. Test: the statistic d̄ ÷ se gives a two-sided p-value from Student's t with n − 1 degrees of freedom.
   Because two comparisons are tested, the *Holm correction* keeps the chance of any false positive
   across the two at 5%: the smaller of the two p-values must be at most 0.025, and then the larger at
   most 0.05.

<!-- src: analysis plan §7.1 l.369-401.
     Step 3, which terms exist at 9b0c680ed: joulewise/analysis_engine/inputs.py l.3852-3903 (governed_stochastic_variance returns no term
     unless the metric is energy_request_j, and then the one term E_idle_mean_j2); joulewise/reduce.py l.445-464 (the two entries a run's
     summary carries; the repetition entry is always empty for a single run); joulewise/analysis_engine/estimators.py l.378-406, l.469-475
     (an empty list gives se_metrology 0). The analysis plan states step 3 in general and does not name the terms. -->

*The floor for a comparison.* For each model, take the larger of its two forms of floor for that phase.
The comparison's floor is the larger of the two models' values. These floors were measured in windows 1
and 2, not in window 3. Using them in window 3 rests on a registered assumption, that the timing behaviour
measured in the null quads carries over to quads of the same length in another window, and the paper
states that assumption and its limit beside the result.
<!-- src: analysis plan §5 l.330-337 -->

*Outcome,* decided in this order:

- **not estimable** if a required input is missing or invalid;
- **not resolvable** if |d̄| is not above the floor, or if the first interval excludes zero but the second
  does not;
- **unresolved** if the first interval contains zero, or the Holm test does not reject;
- **direction supported** otherwise.

A comparison earns **L2** only when its outcome is "direction supported", the direction is the registered
one, and no single quad, when left out, changes the sign of d̄, whether d̄ is above the floor, the Holm
decision or the outcome. Otherwise the result is worded at L1.
<!-- src: analysis plan §7.2 l.405-436 -->

*Worked example (synthetic).* Nine kept quads with d_k = 3.1, 2.9, 3.3, 2.8, 3.2, 3.1, 2.9, 3.0 and
2.7 J. Then d̄ = 3.0 J, s_d = 0.1936 J and se_rep = 0.0645 J. To show step 3 at work, suppose one error
term whose quad variance is 0.0100 J² in every quad: se_met = √(9 × 0.0100 ÷ 81) = 0.0333 J and
se = 0.0726 J. (With no term, as the code stands for gross phase energy, se would be 0.0645 J.) With
t = 2.306, the first interval is 3.0 ± 0.1675, that is 2.83 to 3.17 J. With D = 0.05 J the second is
2.78 to 3.22 J. The statistic is 3.0 ÷ 0.0726 = 41, so p is far below 0.025. With a floor of 1.2 J: d̄ is
above the floor, neither interval contains zero, the test rejects, the direction is the registered one,
and leaving out any one quad moves d̄ by at most 0.04 J. Outcome: direction supported, rung L2.
<!-- src: analysis plan §7.2 l.438-444; calc: scratch recompute -->

Printed beside each comparison, as descriptive figures that decide nothing: the ratio of the two models'
phase energies with an interval, and the difference per token. Also this sentence, because the energies
are gross (section 2.2): part of the difference is the machine's baseline power multiplied by the extra
time the larger model takes.
<!-- src: analysis plan §7.3 l.446-457 -->

## 8. What the paper will not claim

Each of these is a design limit, stated as such.

- **No other prompts.** The decode comparison uses one fixed prompt. Nothing is claimed about prompts in
  general.
- **No other prompt lengths.** Prefill is measured at 2,048 tokens only. The 42-token prefill of the
  decode workload is too short to resolve and is not reported.
- **No other machine, operating system, runtime, model or quantization.** L1 and L2 are statements about
  this exact stack. The higher rungs need held-out cases or a second machine.
- **No wall power and no whole-machine energy.** Every claimed number is processor-package energy. The
  meter's whole-machine figures are a described cross-check, never a claim.
- **No comparison of window 1 with window 2.** Their numbers appear side by side, labelled as collected
  in separate windows in a fixed order.
- **No "no difference".** A difference at or below the floor is "not resolvable".
- **No independent check of phase attribution.** The energy is assigned to phases by the overlap rule of
  section 2.2. No separate experiment characterizes how well that assignment tracks where the energy was
  actually spent: the instrument-characterization campaign that would have done so was omitted by a
  recorded decision. Every phase-energy sentence in the paper carries that limitation.
- **No interval that covers between-window variation.** Intervals describe one window. The order inside
  every quad is fixed, not randomized, and the test assumes that the quad differences are independent.
- **No unconditional number.** Every number is conditional on a window that passed the start check and
  kept 8 of 10 units, and is printed with its attempt history.

<!-- src: registration §1 l.885-894; §7.6 l.2877-2881; analysis plan §8.1 l.470-474, l.512-514, l.527-528, l.561-568; §12 l.679-690; docs/decision_log.md D-177 l.11605-11636 -->

## 9. How the result is kept blind

From the start of the first window until all three windows have a claim-usable attempt (or collection
has been stopped), every report, email and summary carries **structure** only: verdicts, whether an
attempt is claim-usable, counts of flags, counts of kept units, file hashes, the hazard measurements, and
timing that is not the length of a phase. Energies, powers, phase lengths, floors, averages and ratios
stay in storage that only the automated programs read.
<!-- src: registration §8 l.2886-2893 -->

Before anything is unblinded, the analysis programs are run once from end to end on the real data with
their outputs kept unseen. Only whether each step ran, and the hash of what it produced, is visible. Any
tooling fault is fixed at that stage, blind. Then a recorded *release* ties the sealed documents to the
final data, and the analysis runs exactly as registered; its outputs must match the blind run's hashes.
Any analysis not registered in advance is labelled exploratory. The analysis programs themselves are
written by AI model sessions that have read no energy from these windows.
<!-- src: registration §8 l.2894-2897; analysis plan §3.2 l.186-199; §11 l.671-675 -->

## 10. Timing and status

**How long it takes.** The runs of one window are expected to take about 5 to 6 hours: 5.4 h for window
1, 5.7 h for window 2 and 4.8 h for window 3. These projections are built from run times measured in the
earlier prompt-length probe, less the savings of changes made since, and they have not themselves been
measured. With that probe's run times unchanged, the figures are 8.8, 9.1 and 7.7 h. The first window
shows which is right. Each window adds its start check (4 to 47 minutes) and about 0.6 to 1.6 hours
before the next can start, most of it the post-window program.
<!-- src: registration §5.5 l.1848-1852, l.1875-1895, l.1903-1906 -->

Windows run back to back, at any hour of the day or night. The laptop is dedicated to these
measurements, and nothing but the physical checks and the post-window program waits between one window
and the next. If every window is claim-usable on its first attempt, the three take about 18 to 23 hours
at the projected figures and about 28 to 33 hours at the larger ones. That is between two and four
windows in 24 hours, not one. Each attempt that has to be repeated adds one more window.
<!-- src: registration §5.5 l.1903-1909; calc: 3 windows in 18 to 23 h is 3.1 to 4.0 per 24 h; in 28 to 33 h, 2.2 to 2.6 per 24 h -->

One number should not be misread. Each window also carries a *deadline* of 25 to 29 hours. That is the
time after which a hung window is killed. It is sized as if every run took its longest allowed path
(every cooldown at its 300 s cap and every quiet check needing its second try), so that it never cuts
short a slow window that could still be usable. It is not the expected length of a window.
<!-- src: registration §5.5 l.1848-1852 (WINDOW_MAX_S 28.4, 29.05 and 25.3 h), l.1859-1874 -->

**Where things stand on 2026-10-07.** Nothing has been collected and nothing is scheduled.

- The three design documents are at revision 9, in draft.
- The seal is next: an independent ruling by an AI model session that took no part in the design, checked
  by a second session whose only job is to show the ruling wrong. It rules in particular on three things
  this brief describes: the 8-of-10 rule, the effect the catalog gives each flag, and the proposed
  sensitivity line of section 6.4.
- The whole system has been audited by three different AI models, each working alone. Each serious
  finding was then challenged by a model other than the one that raised it. Each confirmed finding has
  been fixed, except those in analysis code that never runs during collection, which are assigned to
  analysis work that must be finished before any energy is read.
- Most of the analysis programs of section 7 are still to be written or adapted to the 8-of-10 rule. That
  work is done blind, after the seal and before the release of section 9. Where the present code cannot
  yet compute a number correctly, it refuses to compute it: for example, it cannot yet hand a floor its
  window's drift allowance, so it issues no floor.
- Open: the binding of the attribution floor (section 2.4); and where these results will be printed. The
  paper drafted so far is a methods paper on timing that prints no result from these windows, and whether
  these results form their own paper or new sections of that one is not decided.

<!-- src: registration §12 l.3095-3102; §9.1 l.2903-2911, l.933-936; §0.12 l.661-669; §14 Q4 l.3300-3301, Q5 l.3302-3303, Q13 l.3341-3346; analysis plan §11 l.656-675 -->

## 11. Where a challenge from you would be most useful

These are the judgment calls in the design, each stated above with its reason. If one looks wrong to a
metrologist, it is cheaper to hear it before the seal than after.

1. **Reduced numbers in place of all-or-nothing windows** (section 6.3): a reported energy may rest on 8
   or 9 units of a kind, with a wider interval and the removals printed.
2. **Battery help reported, not excluded** (section 6.4), with every number printed both ways.
3. **Intervals that cover one window only,** with repeats and quads treated as independent draws
   (sections 3.2 and 7.1), and one registered cross-window check in place of a between-window variance.
4. **A fixed, unrandomized A, B, B, A order** in every quad (sections 3.2 and 7.4).
5. **The competing-process limit of 5% of one core.** It has never been applied to every process on this
   laptop through a whole window. If the first window shows that it costs too many units, the limit is
   retuned from the counts of flags, which are not energies, by a reviewed change made before the next
   window.

<!-- src: registration §14 Q3 l.3296-3299 -->

Sources: the registration, its analysis plan and its flag catalog (in the repository under
`configs/campaigns/v5_claim_25g83/`), revision 9, draft.
