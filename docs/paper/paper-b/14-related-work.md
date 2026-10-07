# 14. Related work

<!--
Draft of 2026-10-07 for the paper wave (work-list item 13). Design text only: no measured value of the
measurement block appears here, and none may be added without a slot from `slots.json`.

Source comments. "src: registration §x l.n" is a line of
`configs/campaigns/v5_claim_25g83/registration_block5.md`, and "src: analysis plan §x l.n" a line of
`analysis_plan_block5.md` in the same directory, both as they stand at commit 9b0c680ed (revision 9, DRAFT, not
sealed). Every registered value in this file carries such a comment so that the post-seal sync can recheck it.

Terms. The plain names are those of `01-terms.md`; each is glossed again where this section first uses it.
"calc:" comments show arithmetic done here; "synthetic" marks invented numbers.

Citations. A bracketed number is an entry of the reference list at the end of this file. What each cited source
was checked to say, with the date and the locator fetched, is in `14a-citation-verification.md`. Quotation marks
enclose a source's exact words; sentence punctuation is kept outside them.
-->

This paper reports how much energy a laptop's processor uses when a large language model (a program that generates
text in reply to a prompt) runs on that laptop, separately for the two phases of answering one request (reading the
prompt, then generating the reply), and how small a difference the measurement can tell apart. Six bodies of earlier
work bear on that design: energy benchmarks (fixed workloads with fixed measurement rules, used to compare systems),
which settled what an energy number must state to be comparable (14.2); studies that check power values computed
inside a machine against meters outside it (14.3); studies of when such a value attributes energy in time (14.4);
per-phase energy studies of language models on data-centre graphics processors (14.5); energy studies of language
models on Apple's own processors (14.6); and the literature on experimental method, including decisions fixed before
the data are seen (14.7 and 14.8). For each, this section says what the earlier work established, what this study
takes from it, and where this study is weaker. Section 14.9 collects the comparison in one table.

The section compares designs and rules only. No measured value of this study is set beside a published value, because
the cited studies measure other machines, other components and other workloads (14.6).

## 14.1 Terms used in this section

The terms below are built in the order the section uses them. The rest of the paper defines them in full; the short
forms here are enough to read the comparison.

**Model, token, phases.** A large language model (LLM) produces text one **token** (a word or a piece of a word) at a
time. Answering one request has two **phases**. In **prefill** the model reads the whole prompt and computes the first
output token. In **decode** it produces the remaining output tokens, one per step.
<!-- src: registration §0.4 l.307-309 -->

**Machine, sampler, power record, processor rails.** Every measurement comes from one Apple M3 Max laptop running on
its 140 W mains adapter. <!-- src: registration §0.2 l.267-268 --> The operating system's `powermetrics` tool, called
the **sampler** in this paper, is asked for one **power record** every 100 ms. A record states the average power, over
the record's own span of time (about 0.13 s in practice), of three supply lines inside the processor package: the CPU,
the GPU and the Neural Engine, which is Apple's machine-learning accelerator. We call these three the **processor
rails**. <!-- src: registration §0.2 l.270-273 --> <!-- rv: member.sampler_rate_hz --> The values are estimates
computed by Apple's software, not readings of an instrument outside the processor. The tool's own manual page says
that its average power values "are estimated and may be inaccurate - hence they should not be used for any comparison
between devices"; a published library for the same machines repeats the first half of that warning [9].
<!-- src: `man powermetrics` on the measurement machine, macOS build 25G83, read 2026-10-07 (14a, part 3) -->

**Runtime, phase energy, phase edge.** The **runtime** is the program that runs the model. The **phase energy** of a
request is the sum, over the power records, of each record's power times the length of time the record overlaps the
phase. Nothing is subtracted for the idle machine. <!-- src: registration §0.4 l.310-312 --> A **phase edge** is the
instant at which a phase starts or ends. The runtime stamps the edges on the machine's clocks, and the sampler labels
its records on its own time axis, so each record has to be placed against the edges. An error in that placement moves
energy across the edge. *Worked example.* With the rails drawing 40 W, a placement error of 5 ms moves at most 0.005 s
× 40 W = 0.2 J from one side of an edge to the other. <!-- src: registration §0.14 l.722 -->
<!-- calc: 0.005 × 40 = 0.2 -->

**Measurement boundary.** The **measurement boundary** of an energy measurement (its boundary, for short) is the set
of components whose energy it includes. Figure 14.1 shows the three places on this laptop at which a measurement can
be taken, and the instrument used at each: a meter at the wall socket, which in the benchmarks below is a **power
analyzer** (a laboratory instrument that measures electrical power with a stated uncertainty); a meter placed in the
adapter's cable (an **inline** meter); and the sampler.

```
 [wall socket]
      |   alternating current         <-- point A: a wall meter or power analyzer
 [adapter, 140 W]
      |   direct current, USB-C cable <-- point B: an inline USB-C meter
 [laptop power input] <-----> [battery]
      |
      +---> [processor rails: CPU, GPU, Neural Engine]   <-- point C: the sampler's estimate
      +---> [rest of the laptop: memory, storage, fans, display (asleep)]
```

*Figure 14.1. Where energy can be measured on the laptop.* Each bracketed box is a component. A vertical line or a
single-headed arrow between boxes shows the direction in which power flows: from the wall socket down through the
adapter into the laptop, and inside the laptop to the processor rails and to everything else. The words beside a
vertical line say what kind of current it carries. The double-headed arrow says that the battery can take power from
the laptop's input (charging) or give power to the laptop (discharging). Each arrow drawn from a label (point A, point
B, point C) to the power path marks a place where a measurement is taken, and the label names the instrument used
there. **Point A**, at the wall, includes every component and also the adapter's conversion loss (the energy the
adapter loses in turning alternating current into direct current). The benchmarks of 14.2 require a measurement there;
this study has none. **Point B**, in the cable between adapter and laptop, includes every component of the laptop but
not the adapter's loss, and it does not see energy the battery supplies. This study places an inline meter there, the
**whole-machine meter**, as a cross-check (14.3). **Point C** is the sampler's estimate for the processor rails, the
quantity in which every result of this study is stated. On the server systems of the works cited in 14.3 to 14.5, the
corresponding place is the report a processor or a graphics card makes of its own power.
<!-- src: registration §5.8 l.2009-2033; §1 l.892-894 -->

**Registration.** The **registration** is the document that states the workloads, the number of repetitions, every
threshold and the analysis; its bytes are frozen through an independent review, and their hash is recorded, before any
of the data it governs exist. We call a document frozen in this way **sealed**.
<!-- src: registration §8 l.2885; §12 l.3095-3100 -->

**Member, quad, window, measurement block.** A **member** is one run of one request in its own process, preceded by a
recording of the idle machine (its **idle baseline**). <!-- src: registration §0.3 l.277-285 --> A **quad** is four
consecutive members in the order A, B, B, A, where A and B are the two things being compared.
<!-- src: registration §0.8 l.418-420 --> A **window** is one unattended stretch of machine time in which a fixed list
of members runs in a fixed order. <!-- src: registration §0.7 l.410-411; §4.1 l.1172 --> A **measurement block** is a
set of windows sealed under one registration. The measurement block this paper reports (block 5 in the repository) has
three kinds of window. In two of them, the **single-model windows**, one model runs alone, Qwen3-1.7B in one and
Qwen3-8B in the other (the 1.7B model and the 8B model), and A and B are the same workload, so that any A-against-B
difference comes from the instrument and the machine. In the third, the **contrast window**, the two models alternate,
A being the smaller; the mean over its quads of the B-minus-A difference in one phase's energy is a **contrast**.
<!-- src: registration §0.7 l.392-394; §0.8 l.425-428 --> Two workloads are measured. The **decode workload** has a
42-token prompt and 512 output tokens and supplies the decode phase; the **prefill workload** has a 2,048-token prompt
and supplies the prefill phase. <!-- src: registration §0.5 l.323-334 -->
<!-- rv: workload.decode.prompt_tokens; workload.decode.output_tokens; workload.prefill.prompt_tokens --> Each
reported phase energy rests on 10 **absolute repeats** (members run on their own, not in a quad) and 10 quads of one
model on one workload; each contrast rests on 10 quads. <!-- src: registration §0.8 l.429-432; §0.9 l.438-443 -->

**Flag, detection floor.** A **flag** is a recorded fact about a window or a member that never stops collection. A
file sealed with the registration, the **flag catalog**, fixes in advance whether each kind of flag removes a member,
removes a window, or is only reported. <!-- src: registration §0.16 l.771-780 --> The **detection floor** of one model
and phase is the largest difference the instrument and the machine produce when nothing differs, estimated from
members that all run the same workload. A contrast whose estimate does not exceed its floor is reported as **not
resolvable**. <!-- src: registration §0.10 l.447-450 -->

## 14.2 Energy benchmarks: a fixed workload, a stated boundary, and rules for the meter

*The problem these works solved.* An energy number can be compared across systems only if the workload, the boundary
and the meter are fixed by rule, in advance, for everyone.

JouleSort [1] is the model. It fixes the workload (sort a fixed number of records), the quantity compared (records
sorted per joule) and the measurement rules. Its boundary is the wall: "All power is measured from the wall and
includes any conversion losses from power supplies", and every hardware component used, "idle or otherwise", must be
included. It requires at least three consecutive energy readings, and its authors measured with a meter of ±1.5%
accuracy read once a second. It also names the difficulty this paper is about, at the scale of a whole run: one reason
it rejects a contest with a fixed energy budget is "inaccuracies in synchronizing readings from a power meter to the
actual runs". SPECpower_ssj2008, from the Standard Performance Evaluation Corporation (SPEC), was the first
industry-standard benchmark of the power and performance of computer systems [2], and the methodology document SPEC
maintains for such benchmarks [3] turns the meter into a rule: the analyzer must report with an overall uncertainty
below 1% for alternating current and 1.5% for direct current, must have been calibrated within the past year against a
standard traceable to a national metrology institute (a **traceable calibration**), and must log at least once a
second. MLPerf Power [4], the power benchmark of the MLCommons consortium, carries these rules to machine-learning
systems: a SPEC-approved power analyzer; a first run that finds the peak current and voltage, so that later runs can
hold the analyzer's measuring ranges fixed (SPEC's methodology explains that readings taken while an analyzer changes
range can be inaccurate or lost [3]); and, for most of its scenarios, at least 60 seconds of power data.

*What this study takes.* Two things. First, the boundary is stated with every number: each reported energy is labelled
as processor-rail energy on this machine, never as wall or whole-machine energy.
<!-- src: registration §1 l.887-894 --> Second, the rules are fixed before collection, in the registration, rather
than chosen after the data are seen (14.8).

*Where this study is weaker.* Its reported number is not an analyzer measurement at all. It is the vendor's estimate
at point C of Figure 14.1, for which no uncertainty of the SPEC kind exists and whose own documentation advises
against comparisons between devices (14.1). The study therefore makes no statement across devices: its strongest
sentence is a comparison of two conditions on one machine, one operating-system build, one runtime and one sampler.
<!-- src: registration §0.19 l.859-863 --> MLPerf Power, for its part, does not yet cover battery-powered mobile
devices, partly because they "cannot be simply connected to an external power source for measurement without altering
normal operation" [4]. A laptop on its adapter is a milder form of the same difficulty: it is connected, but its
battery stays in the circuit.

*The battery.* JouleSort's rule is that if energy is stored in the system, "e.g. in batteries, the net change in
potential energy must be no greater than zero Joules with 95% confidence, or it must be included within the energy
measurement" [1]. SPEC's methodology asks for more: a valid result should come with "proof ... that it is not relying
on stored battery power while the measurement is in progress", and it notes that "some IT equipment may be capable of
consuming more power than an AC power adapter can supply and thus get higher performance by using additional energy
from their battery" [3]. This laptop does what that note describes. In a test on 2026-10-06 the power entering the
laptop peaked at 135.7 W on the 140 W adapter, and the battery supplied current in 126 of the 170 seconds of load, at
up to 5,331 mA. <!-- src: registration §4.2 l.1259-1262; §9.2 l.2994-2995 --> SPEC's condition can therefore not be
promised for the members that draw the most power, and neither can the first half of JouleSort's rule. The registered
design does two things instead.

- *Where the boundary contains the battery, stored energy that is used is included.* This is the second half of
  JouleSort's rule. For the whole-machine cross-check at point B, the battery's discharge (its current times its
  voltage, read once a second) is added to the meter's energy, because the meter cannot see it.
  <!-- src: registration §5.8 l.2027-2028, l.2051-2053 -->
- *Where the boundary does not contain the battery, the design does not rest on an argument silently.* The reported
  number is processor-rail energy, and the battery is outside that boundary. The registration's reasoning is that the
  rails are regulated downstream of the supply (the processor is fed through the laptop's own voltage regulators,
  whichever source feeds them), so the rail energy the sampler reports is the same whether the adapter or the battery
  delivered it. <!-- src: registration §9.2 l.3002-3003 --> That is an argument, not a measurement. So battery current
  is read once a second through every member; a member during which the battery discharges with the adapter connected
  (**battery assist**) is flagged, and every reported value is printed twice, with and without such members; a member
  during which the battery charges or the adapter is lost is removed; and a window does not start while the idle
  machine shows more than 200 mA of battery current in either direction.
  <!-- src: registration §4.2 l.1244-1248, l.1269-1275; §9.2 l.3008-3014 -->
  <!-- rv: arm.battery.limit_ma; monitor.every_s.battery_smc -->

The section on battery evidence gives the measurements behind this rule and what would reopen it.

## 14.3 Checking a power value computed inside the machine against a meter outside it

*The problem.* A power value computed inside the machine is convenient and repeatable. How it relates to the power an
external instrument would read (by a constant offset, by a scale factor, or by something that changes with load) has
to be measured, on each kind of machine.

Two such inside-the-machine sources recur below. **RAPL** (Running Average Power Limit) is the energy counter Intel
processors keep for themselves; **NVML** (the NVIDIA Management Library) is the interface through which an NVIDIA
graphics card reports its own power and energy. Khan et al. [6] found RAPL readings "highly correlated with plug
power" (power at the wall plug) across microbenchmarks, application benchmarks and production datasets, and listed
open issues that include "unpredictable timings". Jay et al. [7] compared several software power meters for CPUs and
GPUs against an external meter. The correlation was strong (about 0.95), but the relation was not a constant offset:
regressing the external meter's power on the software meters' power gave slopes of 1.17 on their CPU benchmarks and
1.18 on their GPU benchmarks, and they conclude that the relation "must be studied for each compute node architecture
or even for each individual compute node". *Worked example with their slope.* If a software meter's reading rises from
100 W to 200 W, a slope of 1.17 puts the external reading 117 W higher, so the gap between the two instruments has
grown by 17 W; no single correction in watts turns one reading into the other.
<!-- calc: 1.17 × 100 = 117; 117 − 100 = 17 --> Cao et al. [8] measured language-processing models with a hardware
power meter and found that software energy estimates "can differ from the hardware power measurements by 20% on
average", with standard deviations twice as large.

*What this study takes.* The lesson that an inside-the-machine estimate needs an outside instrument on the same
machine, and that the relation found is a property of that machine. The registered design places the whole-machine
meter at point B of Figure 14.1; it reports the cable's voltage and current 50 times a second.
<!-- src: registration §5.8 l.2023-2024 --> For each member it registers one quantity that is reported but decides
nothing: the rail energy above the member's idle baseline, divided by the energy that entered the machine above the
same baseline (the meter's energy plus the battery's discharge). <!-- src: registration §5.8 l.2049-2056 --> *Worked
example (synthetic).* During a request the meter reads 860 J more than the idle machine would have drawn over the same
time, and the battery supplies 30 J, so 890 J entered the machine above idle. If the rails account for 712 J above
idle, the ratio is 712 ÷ 890 = 0.80. Leaving the battery out would give 712 ÷ 860 = 0.83 and overstate the rails'
share. <!-- src: registration §5.8 l.2062-2067 -->
<!-- synthetic; calc: 860 + 30 = 890; 712 ÷ 890 = 0.800; 712 ÷ 860 = 0.828 --> In line with Jay et al., this ratio is
reported for each model with its spread, and is never used to correct or rescale a reported energy.
<!-- src: analysis plan §8.2 l.586-600, l.608-609 -->

*Where this study is weaker, and what the cross-check cannot show.* Three limits are registered with it.

1. The meter's boundary is the laptop's power input plus the battery's discharge, not the wall: the adapter's
   conversion loss, which JouleSort and SPEC include, is not measured.
   <!-- src: registration §5.8 l.2021, l.2032-2033 --> The meter is an inline USB-C meter, not a power analyzer of the
   kind SPEC accepts, and the registration states no traceable calibration for it.
2. It never enters a reported energy and never removes a member or a window.
   <!-- src: registration §5.8 l.2091-2092 -->
3. It is computed for whole requests only, not for phases. <!-- src: registration §5.8 l.2046-2047 --> Even at phase
   resolution it could not check what this paper is about. Moving the edge between prefill and decode by a few
   milliseconds takes energy from one phase and gives the same energy to the other (0.2 J in the example of 14.1); the
   request's total, which is all a whole-machine meter can confirm, does not change. Agreement of totals says nothing
   about the split.

A second route to Apple's estimates exists. The Zeus project's library for Apple's processors [9] reads running totals
of energy (cumulative counters, at 1 mJ resolution for most channels) through a private operating-system interface,
instead of reading the sampler's interval averages. It describes the values as "believed to be model-based estimates
derived from utilization, frequency, and voltage, rather than direct power sensor readings". This study does not read
those counters. Since both routes report estimates made by Apple's software, agreement between them would test how the
estimate is read and timed, not how large it should be.

## 14.4 When a counter reports energy late, early, or only part of the time

*The problem.* A phase energy needs more than a correct total. It needs the counter to say *when* the energy was used,
on a time axis that can be laid against the workload's own events.

Hähnel et al. [10] met this for short code paths measured with RAPL. The counter is updated about once a millisecond,
and not at exact intervals, so a code path can start anywhere inside an update interval, and the counter value read at
its start can be up to one interval old. Their answer is alignment: before entering the code path they read the
counter in a loop until it changes, they do the same on leaving, and they subtract the energy of the waiting loop.
Burtscher et al. [11] found the corresponding faults in the built-in power sensor of a GPU: computations that "consume
energy after they have stopped executing", and a sensor that "only performs power readings once in a while". Yang et
al. [12] profiled the built-in power sensor of more than 70 NVIDIA GPUs, with an external meter as reference, and
found that on the A100 and H100 data-centre models "only 25% of the runtime is sampled for power consumption". Dauner
et al. [13] varied how often RAPL and NVML are read. Reading an NVML cumulative energy counter more often than it
updates returns values that have not changed since the last read (**stale reads**). On their consumer-class RTX 4090
the cumulative counter fell short of NVML's own power readings integrated over the same time by 95.4% when read every
0.5 ms, by 75.6% at 10 ms and by 13.3% at 100 ms, and came within 1.6% only at 1 s. They add that workloads with
irregular power "remain more sensitive to where counter updates fall relative to workload boundaries".

*What differs here.* This study's sampler is neither a counter read at chosen instants nor a stream of instantaneous
readings. Each power record is an average over its own span, and the design treats the records as following one
another without gaps: it finds the end of each record by adding up the records' durations.
<!-- src: registration §0.14 l.720-727 --> So the failures above do not arise in the same form, but two questions of
the same family do. We know of no documentation of how a record's average is computed inside its span, and this study
does not test it. And the records' time axis has to be placed against the phase edges, which is the alignment problem
of Hähnel et al. without the option of waiting for the counter: the edge between prefill and decode falls wherever the
model's work puts it.

*What the registered design does instead of aligning: it bounds.* To bound an error is to compute a limit that the
error cannot exceed, and then to act on the limit instead of on a best guess.

- *The placement of every member's records is bounded, or the member is removed.* The sampler labels each record with
  a time of day in whole seconds and an elapsed duration. The end of each record, found by adding up the durations,
  must fall inside the second its label names (with a small tolerance). The set of clock offsets and clock rates (how
  far the sampler's time axis is shifted from the machine's clock, and how much faster or slower it runs) under which
  that holds for every record of a member is computed exactly, and the member is kept only if the worst-case placement
  error that set allows, the **member clock bound**, is at most 5 ms; the section on the clock gives the full rule.
  <!-- src: registration §0.14 l.720-731 --> The construction has a long lineage in timekeeping. The Network Time
  Protocol is the protocol by which computers set their clocks from time servers. It gives each time source an
  interval around the time that source reports (a "correctness interval"), and its clock-selection step finds "an
  intersection interval" on which a majority of the sources agree, on principles it credits to Marzullo and Owicki
  [15], [16]; here every record contributes an interval in which the true placement must lie, and the fit is their
  intersection. Treating an error as unknown but bounded, and reporting the whole set of values consistent with the
  bounds, is the subject of set-membership estimation [17]. The design keeps that character through the analysis: a
  timing bound is added in full to the half-width of a reported interval, not combined with it as if it were one more
  independent random error. <!-- src: analysis plan §4 l.233-247 -->
- *Automatic clock correction is switched off, not relied on.* MLPerf Power synchronises the measured machine and the
  logging machine with the Network Time Protocol [4], and the program that checks its submissions accepts timestamps
  of corresponding events that differ by up to 800 ms [5]. That suits its measurement: 800 ms is 1.3% of its 60 s
  minimum. <!-- calc: 0.8 ÷ 60 = 0.0133 --> A phase edge needs milliseconds, and on a single machine the danger is the
  correction itself, which can jump the clock in the middle of a member. The design turns the operating system's
  automatic setting of the clock from network time servers off before every window, and measures directly that the
  clock was not disturbed. The clock's absolute error enters no energy, because every placement uses time differences
  on one machine. <!-- src: registration §4.4 l.1361-1364; §4.2 l.1197-1198, l.1228-1230 -->
- *Timing error between a commanded load and the records is measured before and after every window.* In a **pulse
  calibration** the GPU is driven through 59 commanded on/off pulses. For each pulse the range of start and end delays
  consistent with the records is fitted, and the largest delay over the 59 is that recording's **pulse timing bound**.
  <!-- src: registration §0.11 l.458-463 --> The number 59 is the smallest n for which the largest of n independent
  draws exceeds the 95th percentile of their distribution with probability at least 0.95. The chance that all n draws
  fall below that percentile is 0.95ⁿ, and 0.95⁵⁹ = 0.0485 is below 0.05 while 0.95⁵⁸ = 0.0510 is not.
  <!-- calc: 0.95^59 = 0.04849; 0.95^58 = 0.05105 --> A limit of this kind, which covers a stated fraction of a
  population with a stated probability whatever the population's distribution, is a distribution-free tolerance limit
  in the sense of Wilks [14]. It holds only as far as the pulses of one recording behave as independent draws.
- *A phase that is too short for the sampler is not reported.* A phase that overlaps fewer than three power records
  is refused. <!-- src: registration §0.4 l.316 --> <!-- rv: reducer.min_phase_records --> The prefill of the decode
  workload's 42-token prompt lasts a few tens of milliseconds, less than one record, and is registered in advance as
  expected to be unresolvable. The prefill that is reported comes from the prefill workload, whose 2,048-token prompt
  is the shortest of four lengths tested beforehand at which every test member of the smaller model had a prefill
  overlapping at least five records. <!-- src: registration §0.5 l.328-334 --> Ma et al. [23], discussed in 14.5,
  state the same kind of limit for their instrument, at 200 ms.

*Where this study is weaker.* The pulses characterise the timing of a GPU load that switches abruptly on and off.
Every phase-energy sentence of this paper carries the registered limitation that phase attribution (the assignment of
energy to the phases) of a request to the model was not itself characterised by a measured instrument check.
<!-- src: registration §1 l.885-886 -->

## 14.5 Per-phase energy of language models on data-centre GPUs

*The problem.* Prefill and decode use the hardware differently, so a per-request energy hides two quantities.

Patel et al. established the distinction for systems that serve many users' requests. Their power characterisation
[19] reads GPU power every 100 ms and identifies the two phases from the shape of the power trace (the series of power
readings over time): a spike at the start of each request, which "generally lasts < 1 second", then lower, stable
power while tokens are generated. Splitwise [18] characterises the prompt phase as compute-intensive (limited by
arithmetic speed) and the token-generation phase as memory-bound (limited by how fast memory can be read), and
proposes running the two phases on different machines. The ML.ENERGY benchmark [20] measures GPU energy by software
and reports it per whole response, and shows the same high-power prefill and low-power decode in a power timeline.

Three works report a per-phase energy, in two different ways.

*By splitting one request's power trace at the phase events.* TokenPowerBench [21] tags each power sample "with the
stage that is active at that moment" and integrates the tagged samples into a prefill energy and a decode energy. Its
paper does not give the sampling interval, the rule that decides the stage of a sample near an edge, a number of
repetitions or an uncertainty; a search of its full text found none.
<!-- the search is recorded in 14a-citation-verification.md, entry 21 -->

*By running the phase alone.* Ruf and Detyniecki [22] isolate prefill "by setting the generation length to exactly 1
token", read GPU power through NVML every 1 ms, and align each reading with the start and end markers their runtime
emits for prefill. Each prompt length is measured in a single run, which they defend by the workload being
deterministic. Decode energy per output token is then obtained from a second run by subtraction: total energy minus
the isolated prefill energy, divided by 128 output tokens. Ma et al. [23] give the most complete measurement
description of the three. Energy per token is "measured separately for prefill and decode"; GPU power is read through
NVML every 50 ms and integrated; operations shorter than 100 ms (about 44% of their prefill configurations) fall back
to one power reading times the elapsed time; the integrals are cross-validated against the GPU's hardware energy
counters, which agree to within 2% for operations of at least 200 ms; each configuration is repeated 10 to 20 times
after three warm-up iterations, and medians are reported.

*What this study takes, and how it differs.* This study uses the first way: it splits the power records of one request
at the edges the runtime stamps (14.1). That measures the two phases of the same request, under the conditions that
request actually had, where the second way measures prefill in one run and infers decode across two. The price is the
edge. Running a phase alone has no edge inside the request to place; splitting a trace has one, and the phase energies
are only as good as its placement. Neither TokenPowerBench's tagging nor Ruf and Detyniecki's alignment to the
runtime's markers comes with a stated bound on that placement. This study's contribution to this line is to make the
bound part of the result: the member clock bound, the minimum of three records and the pulse calibration of 14.4
decide whether a phase energy is reported at all, and the detection floor decides whether a difference between two
phase energies is reported as resolved.

*Where this study is weaker.* It has no second counter for the processor rails with which to cross-check its sums, as
Ma et al. have; its only independent instrument is the whole-machine meter of 14.3, which cannot resolve phases. It
does not run a one-token prefill member, which would give a check on the prefill energy that needs no edge inside the
request; no such member is in the registration. And the works above measure data-centre GPUs, several of them while
serving batches of requests, where this study measures one request at a time on a laptop, so their findings and this
study's answer different deployment questions.

## 14.6 Energy of language models on Apple's processors, and what is already known about model size

Several studies report LLM energy on Apple's processors with the same sampler. AgentStop [24] measures agent workloads
(programs in which a model calls tools over many steps) on an M1 Max laptop, logs `powermetrics` power every 100 ms,
integrates it, subtracts a baseline CPU energy, and reports mean energy per agent run with 95% confidence intervals.
Silicon Showdown [25] integrates `powermetrics` processor power over each task and averages three timed runs after two
untimed ones; it sets these beside NVIDIA cards measured through NVML energy counters, which is a different boundary.
Intelligence per Watt [26] reads GPU power from `powermetrics` every 50 ms, integrates it per query, and divides task
accuracy by power; it states that software-reported power readings "can introduce inaccuracies of 10–15%" and names
the split between prefill and decode energy as future work. GreenBench [27] samples `powermetrics` every two seconds
on an M4 Pro and computes energy per token as one package-power figure (CPU plus GPU) times the time per output token,
with whole-system power taken from specifications rather than measured. Wilkins et al. [28] read `powermetrics` every
200 ms on an M1 Pro, subtract idle power, run their experiments in random order, and repeat each until its mean
runtime is known to within 0.5 s at 95% confidence or 25 trials are reached. Benazir and Lin [29] characterise LLM
latency and throughput on Apple's processors and report no energy.

*How this study differs.* Each of these studies reports energy for a whole task, response or query. We found in none
of them an energy for a single phase, or a bound on how far a sampler record may be misplaced against a workload
event. That is the gap this paper works in: on the same sampler, a per-phase quantity with a stated timing bound, a
measured detection floor, and a second instrument at the laptop's power input. In exchange this study covers far less
ground: two models, one runtime, one fixed decode prompt and one prefill prompt length, where the studies above cover
many models, tasks or devices. Nothing here supports a statement about prompts in general or about prompt lengths
other than the one measured. <!-- src: registration §1 l.886-887 -->

*Model size.* That a larger model uses more energy per token is established, with exceptions. The ML.ENERGY benchmark
reports that "models with more parameters consume more energy, but this is not always the case" on data-centre GPUs
[20], and GreenBench reports lower energy per token for its smaller models on an Apple processor [27]. The contrast
window, which alternates Qwen3-1.7B and Qwen3-8B, registers the same direction (the larger model uses more phase
energy) for both of its contrasts. <!-- src: analysis plan §7.1 l.369-376 --> This paper does not offer that direction
as a finding about model size. The contrasts are there to test the instrument: whether, within one boundary and
against the floors measured in the two single-model windows, a difference in the expected direction is reported as
resolved or as not resolvable, for each phase separately. For that reason, and because the cited studies measure other
machines, boundaries and workloads, no energy value of this study is set beside theirs.

## 14.7 Experimental method: repetition, order, rest, and a quiet machine

*The problem.* Run-to-run variation, slow drift (a gradual change in the machine or the instrument over a session) and
unnoticed features of the setup can each produce a difference that is not an effect of the thing compared.

Georges et al. [30] showed, for Java performance, that prevalent ways of reporting repeated runs "can be misleading,
and can even lead to incorrect conclusions", and argued for statistically rigorous analysis of run-to-run variation.
Mytkowicz et al. [31] showed that "changing a seemingly innocuous aspect of an experimental setup" (the size of the
UNIX environment, the order in which object files are linked) biases a measured effect. They call this **measurement
bias** and propose one technique to avoid it (running each experiment in many randomised setups) and one to detect it
(causal analysis, which establishes that a conclusion holds despite the bias). For energy experiments specifically,
Cruz's guide [32] is a widely used checklist: run nothing else ("zen mode"), freeze and report settings, warm up,
repeat 30 times, rest between measurements (one minute is suggested), shuffle the order, control room temperature,
automate. Among the LLM studies, Fadel Argerich et al. [33] start a run only when GPU power has stayed within a 3 W
range for at least 30 seconds and the GPU is below 65 °C, with a 5-minute limit on the wait.

The registered design follows this list item by item, and departs from it knowingly in three places.

- *A quiet machine, measured.* Running nothing else becomes a set of conditions measured directly before a window may
  start: the clock is undisturbed, the machine is on its adapter and its battery is neither charging nor supplying
  current, the operating system reports no **thermal pressure** (its own indicator that it is limiting performance
  because of heat), no other process uses more than 5% of one core, the disk has room for the window, and the sampler
  delivers records at its rate. These are the six physical hazards of the section on hazards.
  <!-- src: registration §0.15 l.750-753 --> <!-- rv: arm.contention.cpu_limit_s_per_s --> Clock, battery, thermal
  pressure, competing processes and free disk are then recorded throughout the window.
  <!-- src: registration §0.17 l.824-828 --> Each member's idle baseline must in addition pass quietness tests of its
  own before the request runs, and the window runs from the system scheduler with no person at the machine.
  <!-- src: registration §0.13 l.709-716; §4.1 l.1172 -->
- *Warm-up and rest.* Each measured request follows one untimed generation of the same request.
  <!-- src: registration §0.3 l.296 --> Between members the idle machine is read in 5-second readings, and the next
  member starts at the first reading whose mean processor power is at most twice the previous member's idle baseline
  while the operating system reports no thermal pressure, or after 300 s at the latest.
  <!-- src: registration §0.6 l.350-353 -->
  <!-- rv: cooldown.sustained_window_s; cooldown.tolerance_fraction; cooldown.cap_s --> This is the same kind of rule
  as that of Fadel Argerich et al., with the same 5-minute limit, but no temperature reading enters it.
  <!-- src: registration §0.6 l.369 -->
- *Repetition, fixed in advance (first departure).* Each reported value rests on 10 absolute repeats and 10 quads,
  and a value is reported only if at least 8 of each remain once flagged members have been removed.
  <!-- src: registration §0.16 l.792-793 --> <!-- rv: catalog.cell_unit_minimum --> This is fewer than Cruz's 30, and
  it is not a rule that sets the number of repetitions from the data as they arrive, like that of Wilkins et al. The
  count is fixed in the registration, and the registered rule for running a window again is built so that it "cannot
  select on the science outcome". <!-- src: registration §7.6 l.2877-2881 -->
- *Order: A, B, B, A, not shuffled (second departure).* A quad cancels a drift that grows steadily from member to
  member. *Worked example.* If each member reads δ more than the one before, the four positions carry 0, δ, 2δ and 3δ
  of drift; the two A members (first and last) average 1.5δ and the two B members (second and third) average 1.5δ, so
  the A-against-B difference gains nothing. A drift that curves does not cancel: with drift k² at positions k = 0, 1,
  2, 3, side A averages 4.5 and side B 2.5. <!-- src: registration §0.8 l.421-424 -->
  <!-- calc: (0 + 3)/2 = 1.5; (1 + 2)/2 = 1.5; (0 + 9)/2 = 4.5; (1 + 4)/2 = 2.5 --> The order is the same in every
  quad and is not randomised, so the design does not have the protection that Mytkowicz et al. and Wilkins et al.
  obtain from randomisation. Its significance level rests on a model (the quad differences are independent draws once
  steady drift has cancelled), and the paper says so beside each contrast.
  <!-- src: analysis plan §7.1 l.376-377; §7.2 l.429-430; §8.1 l.527-528 -->
- *Drift is measured, not assumed absent.* Every window runs one fixed reference workload, different from both
  measured workloads: 12 times at its start, to learn how much the reference varies by itself, then three times before
  the measured members, once in their middle and three times after them. If the mean of the references run after the
  measured members differs from the mean of those run before them by more than a bound computed from the 12, the
  window is not used; otherwise the observed movement of the references is carried into the uncertainty of every
  reported value. <!-- src: registration §0.12 l.489-495, l.511-534; §0.6 l.380-381 -->
  <!-- rv: pack.ALPHA.reference_corpus_members --> The section on the reference drift check gives the bound and the
  rule for a reference that is lost. We found no reference workload of this kind in the LLM energy studies cited in
  14.5 and 14.6.
- *Temperature (third departure).* JouleSort requires 20 to 25 °C at the system's inlet [1], SPEC's methodology asks
  for a minimum inlet temperature (20 °C is its suggested starting point) read by a sensor good to ±0.5 °C [3], and
  Cruz's guide asks for a controlled room. This study measures no room temperature. It requires the operating system
  to report no thermal pressure before a window starts, reads that indicator every 5 s during the window, and records
  the battery's temperature sensor between members as a diagnostic.
  <!-- src: registration §4.2 l.1279-1282; §0.6 l.372-374 -->
  <!-- rv: arm.thermal.max_level; monitor.every_s.thermal --> The reference workload is what would reveal a slow
  thermal drift; the room itself is unrecorded.

Two further cautions from this literature apply in full. All results come from one machine and one software setup,
which is the situation in which Mytkowicz et al. show that a setup detail can pass for an effect; the paper claims
nothing beyond that setup. And every reported value is conditional on a window that passed the quietness, timing and
drift tests above; the number of attempts each kind of window needed, and why, is printed beside the values.
<!-- src: registration §7.6 l.2879-2881 -->

## 14.8 Decisions fixed before the data: registration, blind analysis, two tests

*The problem.* An analysis chosen after the results are visible can be steered, without any intent to deceive, toward
the result one expected.

Nosek et al. [34] describe the remedy as preregistration: "define the research questions and analysis plan before
observing the research outcomes", so that tests of predictions are kept apart from explanations found afterwards.
MacCoun and Perlmutter [35] argue that more fields should, "like particle physics, adopt blind analysis": hide the
result from the analysts until the analysis is fixed. In machine-learning benchmarking, Zhuang et al. [36]
pre-register the smallest effect a planned comparison can detect (its **minimum detectable effect**) for accuracy
benchmarks that compare a model with a version of itself whose weights are stored at reduced precision. Their rule
lets the data enlarge that effect, when the two versions disagree on more test items than planned, and never shrink
it. Their subject is accuracy, not energy. Holm's procedure [37] (the Holm correction of this paper) tests several
hypotheses one after another while keeping the chance of any false rejection at the stated level, whichever of the
hypotheses are true.

*What this study takes.* All four.

- The registration, the analysis plan and the flag catalog are sealed together before the first window, and analyses
  not in them are labelled exploratory. <!-- src: registration §8 l.2885, l.2894-2897; §12 l.3095 -->
- The measurement block is blind. While it runs, only structure is released: which windows were usable, which flags
  were raised, how many repeats and quads were kept. Energies, powers, phase durations and anything computed from them
  stay unreadable until the block closes and the analysis has been executed end to end on the real files with its
  numeric outputs still locked away. <!-- src: registration §8 l.2886-2897; analysis plan §3.2 l.189-193 --> The
  function that decides from the flags which members and windows are removed reads only each flag's kind, scope and
  time interval, never an energy, and is tested with inputs whose energy fields raise an error if read.
  <!-- src: registration §0.16 l.781-787 -->
- The detection floor plays the part of the minimum detectable effect, with one difference in kind. Zhuang et al.
  compute their threshold from a planning formula before any data; this study measures its floor, from members and
  quads in which nothing differs, inside the same measurement block and under the same registered rules.
  <!-- src: registration §0.10 l.447-450 -->
- The two contrasts (decode and prefill) are tested together, as one set, with Holm's procedure at 0.05.
  <!-- src: analysis plan §7.1 l.374-375, l.399-401 --> *Worked example (synthetic).* With two tests, the smaller
  p-value is doubled, and the larger is replaced by the greater of itself and that doubled value; a test is rejected
  when its adjusted value is at most 0.05. For p-values 0.012 and 0.040 the adjusted values are 0.024 and 0.040: both
  rejected. For 0.030 and 0.040 they are 0.060 and 0.060: neither rejected, although 0.040 alone is below 0.05.
  <!-- synthetic; calc: 2 × 0.012 = 0.024; max(0.024, 0.040) = 0.040; 2 × 0.030 = 0.060; max(0.060, 0.040) = 0.060 -->

*Where this study differs from the benchmarks of 14.2 on bad data.* Under benchmark rules such as those of 14.2, a run
that breaks a rule is not a valid result. Here a window is refused before it starts when a physical condition measured
directly fails (14.7), and for only two reasons that are not physical: a process of the project's own development
tooling is still running on the machine, or the operating-system build is one on which the pulse calibration was never
judged. <!-- src: registration §4.1 l.1187-1188; §4.5 l.1368-1371; §4.7 l.1511-1518 --> Every other irregularity is
recorded as a flag, and the sealed flag catalog, not a decision made after looking, says whether that flag removes a
member, removes a window, or is disclosed beside the result.
<!-- src: registration §0.15 l.758-767; §0.16 l.775-780 -->

## 14.9 The comparison in one table

Each row is one practice. The second column is the rule or practice in the cited work; the third is what the
registered design of this study does; the last says how the two relate. *Weaker* means this study does less than the
cited rule asks.

| Practice | In the cited work | In this study's registered design | Relation |
|---|---|---|---|
| Boundary | Wall power, including power-supply loss and every component [1], [3] | Reported value: processor rails as estimated by the sampler. Cross-check: laptop power input plus battery discharge; adapter loss not measured <!-- src: registration §1 l.887-894; §5.8 l.2032-2033 --> | Narrower; stated with every number |
| Meter accuracy | Analyzer uncertainty below 1% (AC) or 1.5% (DC), calibrated within a year [3]; ±1.5% meter [1] | None stated for the sampler, whose documentation calls its values estimates; cross-check meter without traceable calibration, reported only | Weaker |
| Battery | Net change in stored energy "no greater than zero", or included in the measurement [1]; proof that the battery is not relied on [3] | Battery current read every second; charging or loss of the adapter removes the member; discharge on the adapter is flagged and each value printed with and without those members; discharge added to machine energy <!-- src: registration §9.2 l.3008-3014; §5.8 l.2027-2028 --> | Differs; SPEC's condition is not met for the members that draw the most power |
| Time alignment | Network time synchronisation, 800 ms tolerance [4], [5]; start and end aligned to counter updates [10] | Automatic network time off; member clock bound of at most 5 ms, or the member is removed; pulse calibration before and after each window <!-- src: registration §4.4 l.1361; §0.14 l.730-731; §0.11 l.458-463 --> | Bound instead of alignment, at phase scale |
| Shortest measurable span | At least 60 s of power data [4]; counter agreement from 200 ms [23] | A phase must overlap at least 3 power records of about 0.13 s each <!-- src: registration §0.4 l.316; §0.2 l.271 --> | Same kind of rule, at phase scale |
| Repetition | 3 readings [1]; 30 [32]; 10 to 20 [23]; until a confidence criterion, at most 25 [28] | 10 absolute repeats and 10 quads per reported value, fixed before collection; at least 8 of each must remain <!-- src: registration §0.8 l.432; §0.16 l.792-793 --> | Fixed in advance; fewer than [32] |
| Order | Shuffled [32]; randomised [28], [31] | Fixed A, B, B, A; not randomised <!-- src: analysis plan §7.1 l.376 --> | Weaker on randomisation; cancels steady drift |
| Rest between runs | One minute [32]; power within 3 W for 30 s and below 65 °C, 5-minute limit [33] | First 5 s reading at most twice the previous idle baseline with no thermal pressure; 300 s limit <!-- src: registration §0.6 l.350-353 --> | Same kind of rule; no temperature reading |
| Temperature | 20 to 25 °C at the inlet [1]; minimum inlet temperature, sensor good to ±0.5 °C [3]; controlled room [32] | No room temperature; no thermal pressure at start, indicator read every 5 s; battery temperature recorded <!-- src: registration §4.2 l.1279-1282; §0.6 l.372-374 --> | Weaker |
| Drift within a session | Not found in the LLM energy studies cited | Reference workload 12 times at the start, then three times before, once in the middle of and three times after the measured members; window unused if the references moved beyond a bound <!-- src: registration §0.12 l.489-495, l.527-529 --> | Added |
| Decisions before data | Preregistration [34]; blind analysis [35]; pre-registered detectable effect [36] | Registration, analysis plan and flag catalog sealed before collection; energies unreadable until the measurement block closes <!-- src: registration §8 l.2885-2897 --> | Adopted |
| Several tests | Holm's procedure [37] | The two contrasts tested together with Holm's procedure at 0.05 <!-- src: analysis plan §7.1 l.374-375 --> | Adopted |

## References for this section

1. S. Rivoire, M. A. Shah, P. Ranganathan, and C. Kozyrakis. "JouleSort: A Balanced Energy-Efficiency Benchmark."
   *Proceedings of the 2007 ACM SIGMOD International Conference on Management of Data*, 2007, pp. 365–376.
   DOI:10.1145/1247480.1247522.
2. K.-D. Lange. "Identifying Shades of Green: The SPECpower Benchmarks." *IEEE Computer* 42(3), 2009, pp. 95–97.
   DOI:10.1109/MC.2009.84.
3. Standard Performance Evaluation Corporation, SPECpower Committee. *Power and Performance Benchmark Methodology*,
   V2.3, 12 June 2025. https://www.spec.org/power/docs/SPEC-Power_and_Performance_Methodology.pdf.
4. A. Tschand et al. "MLPerf Power: Benchmarking the Energy Efficiency of Machine Learning Systems from μWatts to
   MWatts for Sustainable AI." *2025 IEEE International Symposium on High Performance Computer Architecture (HPCA)*,
   2025, pp. 1201–1216. DOI:10.1109/HPCA61900.2025.00092; arXiv:2410.12032.
5. MLCommons. *power-dev* (software), file `compliance/check.py`, commit `3785ea1` of 2025-02-20.
   https://github.com/mlcommons/power-dev/blob/3785ea13643f39b8a48c78040e004c7d7c9cd7a4/compliance/check.py.
6. K. N. Khan, M. Hirki, T. Niemi, J. K. Nurminen, and Z. Ou. "RAPL in Action: Experiences in Using RAPL for Power
   Measurements." *ACM Transactions on Modeling and Performance Evaluation of Computing Systems* 3(2), 2018, pp. 1–26.
   DOI:10.1145/3177754.
7. M. Jay, V. Ostapenco, L. Lefèvre, D. Trystram, A.-C. Orgerie, and B. Fichel. "An Experimental Comparison of
   Software-Based Power Meters: Focus on CPU and GPU." *2023 IEEE/ACM 23rd International Symposium on Cluster, Cloud
   and Internet Computing (CCGrid)*, 2023, pp. 106–118. DOI:10.1109/CCGrid57682.2023.00020; HAL:hal-04030223.
8. Q. Cao, A. Balasubramanian, and N. Balasubramanian. "Towards Accurate and Reliable Energy Measurement of NLP
   Models." *Proceedings of SustaiNLP: Workshop on Simple and Efficient Natural Language Processing*, 2020, pp.
   141–148. DOI:10.18653/v1/2020.sustainlp-1.19.
9. ML.ENERGY Initiative. *zeus-apple-silicon* (software), `README.md`, commit `70e8956` of 2026-04-02.
   https://github.com/ml-energy/zeus-apple-silicon/blob/70e895691cfdeacdcb851c8f8d15d1458528e021/README.md.
10. M. Hähnel, B. Döbel, M. Völp, and H. Härtig. "Measuring Energy Consumption for Short Code Paths Using RAPL." *ACM
    SIGMETRICS Performance Evaluation Review* 40(3), 2012, pp. 13–17. DOI:10.1145/2425248.2425252.
11. M. Burtscher, I. Zecena, and Z. Zong. "Measuring GPU Power with the K20 Built-in Sensor." *Proceedings of Workshop
    on General Purpose Processing Using GPUs (GPGPU-7)*, 2014, pp. 28–36. DOI:10.1145/2576779.2576783.
12. Z. Yang, K. Adámek, and W. Armour. "Accurate and Convenient Energy Measurements for GPUs: A Detailed Study of
    NVIDIA GPU's Built-In Power Sensor." *SC24: International Conference for High Performance Computing, Networking,
    Storage and Analysis*, 2024, pp. 1–17. DOI:10.1109/SC41406.2024.00028; arXiv:2312.02741 (under the title
    "Part-time Power Measurements: nvidia-smi's Lack of Attention").
13. M. Dauner, M. Steinberg, A. Brunnert, B. Schicker, and B. Zönnchen. "Evaluating the Influence of Measurement
    Frequency on Energy Readings Using Intel RAPL and NVIDIA NVML." *HotCarbon '26*, July 2026; to appear in *ACM
    SIGENERGY Energy Informatics Review* 6(2). https://hotcarbon.org/assets/2026/paper-46.pdf.
14. S. S. Wilks. "Determination of Sample Sizes for Setting Tolerance Limits." *The Annals of Mathematical Statistics*
    12(1), 1941, pp. 91–96. DOI:10.1214/aoms/1177731788.
15. K. Marzullo and S. Owicki. "Maintaining the Time in a Distributed System." *Proceedings of the Second Annual ACM
    Symposium on Principles of Distributed Computing (PODC '83)*, 1983, pp. 295–305. DOI:10.1145/800221.806730.
16. D. Mills, J. Martin (Ed.), J. Burbank, and W. Kasch. "Network Time Protocol Version 4: Protocol and Algorithms
    Specification." RFC 5905, June 2010. DOI:10.17487/RFC5905.
17. M. Milanese and A. Vicino. "Optimal Estimation Theory for Dynamic Systems with Set Membership Uncertainty: An
    Overview." *Automatica* 27(6), 1991, pp. 997–1009. DOI:10.1016/0005-1098(91)90134-N.
18. P. Patel, E. Choukse, C. Zhang, A. Shah, Í. Goiri, S. Maleki, and R. Bianchini. "Splitwise: Efficient Generative
    LLM Inference Using Phase Splitting." *2024 ACM/IEEE 51st Annual International Symposium on Computer Architecture
    (ISCA)*, 2024, pp. 118–132. DOI:10.1109/ISCA59077.2024.00019; arXiv:2311.18677.
19. P. Patel, E. Choukse, C. Zhang, Í. Goiri, B. Warrier, N. Mahalingam, and R. Bianchini. "Characterizing Power
    Management Opportunities for LLMs in the Cloud." *Proceedings of the 29th ACM International Conference on
    Architectural Support for Programming Languages and Operating Systems (ASPLOS '24), Volume 3*, 2024, pp. 207–222.
    DOI:10.1145/3620666.3651329; arXiv:2308.12908 (under the title "POLCA: Power Oversubscription in LLM Cloud
    Providers").
20. J.-W. Chung, J. J. Ma, R. Wu, J. Liu, O. J. Kweon, Y. Xia, Z. Wu, and M. Chowdhury. "The ML.ENERGY Benchmark:
    Toward Automated Inference Energy Measurement and Optimization." NeurIPS 2025 Datasets and Benchmarks Track (venue
    as given in the arXiv record). arXiv:2505.06371; https://arxiv.org/abs/2505.06371.
21. C. Niu, W. Zhang, J. Li, Y. Zhao, T. Wang, X. Wang, and Y. Chen. "TokenPowerBench: Benchmarking the Power
    Consumption of LLM Inference." *Proceedings of the AAAI Conference on Artificial Intelligence* 40(38), 2026, pp.
    32582–32590. DOI:10.1609/aaai.v40i38.40535; arXiv:2512.03024.
22. B. Ruf and M. Detyniecki. "The Cost of Context: Profiling the Energy Footprint of Input Tokens in Large Language
    Models." *HotCarbon '26*, July 2026; to appear in *ACM SIGENERGY Energy Informatics Review*.
    https://hotcarbon.org/assets/2026/paper-17.pdf.
23. B. Ma, A. Afzal, J. Eitzinger, and G. Wellein. "The Illusion of Power Capping in LLM Decode: A Phase-Aware Energy
    Characterisation Across Attention Architectures." arXiv preprint, 2026. arXiv:2605.11999;
    https://arxiv.org/abs/2605.11999.
24. D. Pham, K. Katevas, A. Shahin Shamsabadi, and H. Haddadi. "AgentStop: Terminating Local AI Agents Early to Save
    Energy in Consumer Devices." *Proceedings of the ACM Conference on AI and Agentic Systems (CAIS '26)*, 2026, pp.
    1051–1069. DOI:10.1145/3786335.3813163; arXiv:2605.15206.
25. A. Javat and A. Kazakov. "Silicon Showdown: Performance, Efficiency, and Ecosystem Barriers in Consumer-Grade LLM
    Inference." arXiv preprint, 2026. arXiv:2605.00519; https://arxiv.org/abs/2605.00519.
26. J. Saad-Falcon, A. Narayan, et al. "Intelligence per Watt: Measuring Intelligence Efficiency of Local AI." arXiv
    preprint, version 7, 2026 (the arXiv record lists NeurIPS 2026). arXiv:2511.07885;
    https://arxiv.org/abs/2511.07885.
27. R. Kannan, R. Firke, S. Bengle, and S. Deshmukh. "GreenBench: Benchmarking Energy Efficiency and Carbon Footprint
    of Open-Source LLM Inference on Apple Silicon." arXiv preprint, 2026 (the arXiv record lists IEEE ICCUBEA 2026).
    arXiv:2608.28667; https://arxiv.org/abs/2608.28667.
28. G. Wilkins, S. Keshav, and R. Mortier. "Hybrid Heterogeneous Clusters Can Lower the Energy Consumption of LLM
    Inference Workloads." *The 15th ACM International Conference on Future and Sustainable Energy Systems (e-Energy
    '24)*, 2024, pp. 506–513. DOI:10.1145/3632775.3662830; arXiv:2407.00010.
29. A. Benazir and F. X. Lin. "Benchmarking and Characterization of Large Language Model Inference on Apple Silicon."
    *Proceedings of the ACM on Measurement and Analysis of Computing Systems* 9(3), 2025, pp. 1–26.
    DOI:10.1145/3771563.
30. A. Georges, D. Buytaert, and L. Eeckhout. "Statistically Rigorous Java Performance Evaluation." *Proceedings of
    the 22nd Annual ACM SIGPLAN Conference on Object-Oriented Programming Systems, Languages and Applications (OOPSLA
    '07)*, 2007, pp. 57–76. DOI:10.1145/1297027.1297033.
31. T. Mytkowicz, A. Diwan, M. Hauswirth, and P. F. Sweeney. "Producing Wrong Data Without Doing Anything Obviously
    Wrong!" *Proceedings of the 14th International Conference on Architectural Support for Programming Languages and
    Operating Systems (ASPLOS XIV)*, 2009, pp. 265–276. DOI:10.1145/1508244.1508275.
32. L. Cruz. "Green Software Engineering Done Right: a Scientific Guide to Set Up Energy Efficiency Experiments." Web
    article, 10 October 2021. https://luiscruz.github.io/2021/10/10/scientific-guide.html.
33. M. Fadel Argerich, J. Fürst, and M. Patiño-Martínez. "Watt Counts: Energy-Aware Benchmark for Sustainable LLM
    Inference on Heterogeneous GPU Architectures." arXiv preprint, 2026. arXiv:2604.09048;
    https://arxiv.org/abs/2604.09048.
34. B. A. Nosek, C. R. Ebersole, A. C. DeHaven, and D. T. Mellor. "The Preregistration Revolution." *Proceedings of
    the National Academy of Sciences* 115(11), 2018, pp. 2600–2606. DOI:10.1073/pnas.1708274114.
35. R. MacCoun and S. Perlmutter. "Blind Analysis: Hide Results to Seek the Truth." *Nature* 526(7572), 2015, pp.
    187–189. DOI:10.1038/526187a.
36. Z. Zhuang, Y. Li, and Z. Fan. "Pre-Registering the Detectable Effect: A Paired-MDE Budget for 4-bit Quantization
    Benchmarks, with a Pilot Audit." arXiv preprint, 2026. arXiv:2605.28873; https://arxiv.org/abs/2605.28873.
37. S. Holm. "A Simple Sequentially Rejective Multiple Test Procedure." *Scandinavian Journal of Statistics* 6, 1979,
    pp. 65–70. https://www.jstor.org/stable/4615733.
