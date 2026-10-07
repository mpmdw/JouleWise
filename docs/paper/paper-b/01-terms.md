# Terms, built in the order they are used

<!--
Paper B lexicon (paper work-list item 3). Conventions for whoever edits this file:
1. A term is set in bold exactly once, at the sentence that builds it, and is never used above that sentence.
   Headings are navigation and are exempt. Bold is used for nothing else.
2. Every number is accounted for by a comment in its own paragraph:
   "src:" names the section and line(s) it was read from, in the registration or the analysis plan
   (configs/campaigns/v5_claim_25g83/registration_block5.md and analysis_plan_block5.md, revision 9, DRAFT, as they
   stand at commit 9b0c680ed) or in a named repository file;
   "calc:" shows arithmetic done here on sourced numbers; "synthetic:" lists invented example values.
   After the seal, every "src:" line must be re-read against the sealed text.
3. A repository label (a code name, a file path, a flag code) appears once, in parentheses, where its plain name is
   built. Lane, decision, directive and session identifiers never appear outside parentheses.
4. No sentence states or hints at a result of the three windows this paper reports.
The mechanical check of rules 1 to 3 is check_terms.py in the notes directory of item 3.
-->

This section builds the vocabulary of the paper. Each term is built from something physical (a part of the machine, a
file, an instant, a number and the arithmetic that produces it) before it is used, and later sections use a term only
if it is built here or at their own first use of it. A term is set in bold once, at the sentence that builds it. Where
the project's repository calls the same thing by another name, that name follows once in parentheses, so that a
reader who opens the repository can find it. The paper itself uses the plain name.

The paper reports how much electrical energy the processor of one laptop spends while a language model, running on
that laptop, reads an input text and writes an answer, and how that energy divides between the reading and the
writing. Every number in this section is either a design value fixed before data collection or a measurement from
earlier sessions on the same machine. None is a result of the paper.

## 1. Fixing the design before the data

A measurement whose rules can change after the numbers are seen can be steered toward a wanted answer, even without
intent. The paper's defence is to write the rules down first and to make every later change visible.

A **claim** is a sentence of the paper that reports a measured result.

The **registration** is the document, written before any of the paper's energy data existed, that fixes what is
measured, in what order, with which thresholds, and which recorded conditions take data out of a claim (repository
file `configs/campaigns/v5_claim_25g83/registration_block5.md`). A value or a rule is **registered** when the
registration states it.

The **analysis plan** is the registration's companion. It fixes every formula applied to the collected data, the
order of the computations, and what is printed (repository file `analysis_plan_block5.md`, in the same directory).

To **pin** a file is to write its SHA-256 digest into a record that is kept, so that any later change to the file's
bytes can be detected by recomputing the digest.

An **agent session** is one running instance of an AI model working as a software agent: it reads files, runs
commands and writes text or code. This project uses agent sessions to draft and review its documents and code and to
run the steps between measurements. Two later terms exist because of them: who may rule on a document (next
paragraph), and what may be running on the machine during a measurement (Section 11).
<!-- src: registration preamble l.3; §0.1 l.247-249; §3 l.1154-1156 -->

To **seal** the registration, the analysis plan and their companion files is to freeze them through an independent
ruling. A judge that took no part in writing them rules on whether they may stand. A refuter, whose only job is to
show that ruling wrong, challenges it. When the ruling stands, every sealed file is pinned in one seal record
(repository label for this judge-and-refuter procedure: cold gate). In this project the judge and the refuter are
separate agent sessions. The seal comes before the first measurement that can feed a claim. After it, a rule changes
only by an **erratum**: a dated amendment made through the same procedure, with one judge and one refuter. An erratum
is **prospective** when it is made before the data it governs exist.
<!-- src: registration preamble l.10; §0.1 l.251-254; §10 l.3033-3034; §12 l.3095-3098 -->

## 2. The machine and its power instrument

Everything in the paper happens on one machine: an Apple M3 Max laptop (model identifier Mac15,9) running macOS build
25G83, powered by a 140 W mains adapter.
<!-- src: registration §0.2 l.267-268 -->

Its processor chip holds the CPU, the GPU and a neural-network accelerator that Apple calls the Neural Engine (ANE).
The operating system reports the electrical power drawn by each of the three. The paper calls those three reported
channels the **processor rails** (a rail is a power supply line inside a computer), and calls their sum **processor
power** (repository field `combined_power_w`).
<!-- src: registration §0.2 l.272-273; §1 l.889-890 -->

The **sampler** is macOS `powermetrics`, a tool shipped with the operating system. The paper's programs ask it for one
reading every 100 ms. A **power record** is one such reading: the average processor power over one short stretch of
time. From here on, "record" alone means a power record. A record's **support interval** is that stretch. The record
says nothing about how power moved inside its support interval, and nothing about any instant outside it.
<!-- src: registration §0.2 l.270-273 -->

The **October probe** is a set of earlier measurement sessions on this same machine, run on 3 and 4 October 2026
(repository label: block 3). Its purpose is built in Section 5. Until then it appears only as the source of timing
figures.
<!-- src: registration §0.7 l.413 -->
<!-- calc: the dates 3 and 4 October 2026 restate 2026-10-03/04 -->

The sampler never reads faster than it is asked to, and on this machine its records are longer than asked. In the
October probe's 37 recordings of the idle machine a record arrived about every 130.5 ms on average, between 130.2 and
132.1 ms from one recording to another.
<!-- src: registration §0.2 l.270-271; §0.3 l.287-288 -->

A **measurement boundary** is the set of components whose energy an instrument's reading includes. The sampler's
measurement boundary is the processor rails. Every energy the paper reports is therefore energy of the processor
rails. It leaves out the memory, the storage, the fans, the display and the adapter's own conversion loss, and it is
never the energy of the whole machine or the energy drawn from the wall.
<!-- src: registration §1 l.892-893; §5.8 l.2016-2017, 2021 -->

## 3. One run: the member

The smallest thing the paper measures is one answer by one model.

A language model reads and writes text as **tokens**: pieces of text, each a word or part of a word. A **prompt** is
the sequence of tokens given to the model as input. A **request** is one prompt handed to a language model running on
the machine, together with the output tokens the model generates in reply.

A **member** is one run of one request in its own operating-system process. It is called a member because it is one
member of a planned set; Section 6 builds the sets.
<!-- src: registration §0.3 l.277 -->

Throughout the paper a program **refuses** when it declines to go on, or to produce a number, and records the reason,
instead of continuing on input it cannot trust.

A member goes through six steps, always in this order.

1. Preparation. The process readies the model runtime (the software that executes the model) and loads the model.
2. The **idle baseline**. The sampler records the idle machine for a fixed number of power records.
3. The **warm-up**. The model answers the same request once, untimed, so that the next answer does not pay one-time
   start-up costs.
4. The **measured request**. The model answers the request again. This is the answer whose energy is reported.
5. Cleanup. The model runtime releases what it holds.
6. Reduction. The **reducer**, a program that reads the raw power records and the recorded instants of each step,
   computes the member's summary (repository file `joulewise/reduce.py`).
<!-- src: registration §0.3 l.279-303; joulewise/controller.py l.31-32; joulewise/interfaces.py l.345, 360 -->
<!-- calc: steps 1, 2, 3, 4, 5, 6 are list numbers -->

The idle baseline is fixed as a count of records, not as a duration: 576 records in every member of this paper. The
count is set as if a record arrived every 100 ms, and 57.6 s of such records is 576. Since a record in fact arrives
about every 130.5 ms, 576 records last about 75 s; over the October probe's 37 idle recordings the median would have
been 75.2 s.
<!-- src: registration §0.3 l.285-290 -->
<!-- calc: 57.6 / 0.1 = 576; 576 x 0.1305 = 75.2, which is about 75 -->

**Idle admission** is the test, applied to each idle baseline before the member goes on to its warm-up, of whether
the machine was quiet while that baseline was recorded. It has two parts. The first is a list of machine states that
must all hold: the machine is on AC power with an external adapter connected, its displays are asleep, no screensaver
is running, Low Power Mode is off, and the operating system reports its thermal state as nominal (it is not slowing
the processor to shed heat; when it is, the state is called thermal pressure). The second is two limits on activity
during the baseline, taken over the baseline's own records, of which there must be at least 30. Beside its power,
each record of the sampler reports, for every CPU core, the fraction of the record's time that the core was idle and
the fraction it was powered down. The record's CPU busy ratio is one minus those two fractions, taken for the busiest
core. The limits are that the 95th percentile of the CPU busy ratio over the baseline's records is at most 0.5, and
that the 95th percentile of processor power over the same records is at most 1.0 W. If either part fails, idle
admission refuses the baseline. A refused baseline is recorded again once, immediately. A second refusal aborts the
member: its request never runs, and only that member is dropped.
<!-- src: registration §0.13 l.709-716; joulewise/idle_admission.py l.344-377; joulewise/adapters/powermetrics.py l.311-318 -->

Worked example. On a machine that holds every listed state, a baseline whose busy-ratio samples have a 95th
percentile of 0.31 and whose processor power has a 95th percentile of 0.42 W passes idle admission, because 0.31 is
at most 0.5 and 0.42 is at most 1.0. A baseline with a busy-ratio 95th percentile of 0.576 is refused, because 0.576
exceeds 0.5. That second value is a real one: it is what one stored recording of the October probe gave when the test
was applied afterwards to its first 75 s.
<!-- src: registration §0.13 l.711-712; §0.3 l.293-295 -->
<!-- synthetic: 0.31 and 0.42 are invented -->

In the October probe a measured request lasted between 11.1 and 23.6 s.
<!-- src: registration §0.3 l.297 -->

The **sampler stream** of a member is one continuous run of the sampler, from the start of the idle baseline to the
end of the measured request. An idle baseline that is recorded a second time stays inside the same sampler stream,
so it makes the stream longer. Section 8 shows why the length of the stream matters.
<!-- src: registration §0.3 l.300-302 -->

The **bundle** of a member is its directory of raw files, recorded instants and summary. Every file in it is written
once and never changed.
<!-- src: registration §0.3 l.303 -->

The steps of one member, drawn in time order:

```
 steps:    preparation | idle baseline | warm-up | measured request | cleanup | reduction
 sampler:              |<--------------- sampler stream ----------->|
 time:    ------------------------------------------------------------------------------->
```

The top line names the six steps from left to right; each vertical bar on it is the instant one step ends and the
next begins. The middle line shows, between its two arrowheads, the part of the member during which the sampler runs:
it starts with the idle baseline and ends with the measured request. The bottom arrow is the direction of time. Widths
are not to scale.
<!-- calc: six steps, as listed above -->

## 4. Phases and phase energy

Answering a request has two parts that load the processor differently. First the model reads the whole prompt at
once. Then it writes its answer one token at a time. The paper reports the energy of each part separately, which
means cutting one sampler stream at an instant.

A **phase** is a named part of the measured request with a recorded start and end. There are two. **Prefill** is the
phase in which the model reads the whole prompt and computes the first output token; it ends when that first token is
emitted. **Decode** is the phase in which the model produces the remaining output tokens, one after another. A **phase
edge** is the instant at which a phase starts or ends.
<!-- src: registration §0.4 l.307-309 -->

**Phase energy** is the energy the processor rails delivered during one phase. It is computed from power records by
one rule: each record contributes its power multiplied by the length of the overlap between its support interval and
the phase. A record wholly inside the phase counts in full. A record that straddles a phase edge counts in proportion
to its overlap. A record outside the phase counts zero (repository function `_integrate` in the reducer).
<!-- src: registration §0.4 l.310-312 -->

Worked example, with invented values. A phase runs from 10.00 s to 10.25 s. Record 1 covers 9.90 to 10.03 s at 20 W:
its overlap with the phase is 0.03 s, so it contributes 20 × 0.03 = 0.60 J. Record 2 covers 10.03 to 10.16 s at 30 W:
overlap 0.13 s, 3.90 J. Record 3 covers 10.16 to 10.29 s at 30 W: overlap 0.09 s, 2.70 J. The phase energy is
0.60 + 3.90 + 2.70 = 7.20 J.
<!-- src: registration §0.4 l.313-315 -->
<!-- calc: 20 x 0.03 = 0.60 -->

```
time (s)  9.90              10.00 10.03                     10.16             10.25   10.29
          |                   |     |                         |                 |       |
records   |----- record 1: 20 W ----|----- record 2: 30 W ----|----- record 3: 30 W ----|
phase                         |=================== the phase ===================|
overlap                       |0.03 |          0.13           |      0.09       |
```
<!-- src: registration §0.4 l.313-315 -->
<!-- calc: record numbers 1, 2, 3 are labels -->

The top two lines are the time axis, in seconds, with a tick at each instant the example uses. On the line marked
"records", each stretch between two vertical bars is the support interval of one power record, labelled with that
record's power. On the line marked "phase", the double line between two vertical bars is the phase, and the bars are
its two phase edges. On the line marked "overlap", each number is the length in seconds of the overlap between the
record above it and the phase. The drawing is to scale.

This energy is **gross energy**: nothing is subtracted for the power the machine would have drawn anyway while idle.
The gross energy of a measured request is found by the same rule, applied to the whole span of the request: from the
instant the measuring program hands the request to the model runtime to the instant the runtime returns with the
answer complete. That span contains both phases. The **idle-subtracted energy** of a measured request is its gross
energy minus the mean power of its idle baseline multiplied by the length of that span (repository field
`idle_subtracted_energy_j`). For example, a request of 20 s with a gross energy of 800.00 J, after an idle baseline
that averaged 0.037 W, has an idle-subtracted energy of 800.00 − 0.037 × 20 = 799.26 J. Every reported phase energy
is gross. Idle-subtracted energy enters only two checks built later, in Sections 9 and 11.
<!-- src: registration §0.4 l.312; §0.6 l.359; joulewise/reduce.py l.2957-2962; joulewise/controller.py l.2338-2343, 2366-2374 -->
<!-- synthetic: 20 s and 800.00 J are invented; calc: 0.037 x 20 = 0.74; 800.00 - 0.74 = 799.26 -->

The reducer needs at least 3 power records overlapping a phase. With fewer it refuses that phase and reports no
energy for it. Each phase also carries a **precheck**: a list of pass-or-fail tests of whether the phase's records and
recorded instants are good enough to compute its energy from. Among them: at least 3 records overlap the phase; the
records arrived regularly; and the error in lining the member's records up in time with its phase edges, for which
Section 8 builds an upper limit, is at most a quarter of the phase's length. The complete list is in the repository
(the names in `_METRIC_LOCAL_PRECHECK_REASONS`, file `joulewise/whole_window.py`).
<!-- src: registration §0.4 l.316-319; joulewise/reduce.py l.976-998; joulewise/whole_window.py l.266-281 -->

## 5. Models and workloads

The paper measures two language models of one openly released family: Qwen3-1.7B and Qwen3-8B. The names give their
sizes, about 1.7 and 8 billion parameters (the numbers a model is made of). Each is used with its parameters stored
at 4 bits apiece, a compressed form called 4-bit quantization, and is run by MLX, Apple's framework for running
models on its own chips (repository identifiers `mlx-community/Qwen3-1.7B-4bit` and `mlx-community/Qwen3-8B-4bit`).
The paper calls them the **1.7B model** and the **8B model**.
<!-- src: registration §0.7 l.392-393; §4.6 l.1433-1434 -->
<!-- calc: 1.7 and 8 billion parameters, and 4 bits, restate the model names Qwen3-1.7B, Qwen3-8B and 4-bit -->

A **workload** is a fixed prompt together with a fixed rule for how much output is generated. The two models are each
measured on two.

The **decode workload** has one fixed prompt of 42 tokens, with the model's optional reasoning output switched off,
and an output forced to exactly 512 tokens: the model always takes its most probable next token, which makes the
output repeatable, and it is not allowed to stop early. Prefill computes the first of those 512 tokens, so the decode
phase covers the other 511 generation steps. An energy per output token divides the decode phase energy by all 512.
<!-- src: registration §0.5 l.323-327 -->

The prefill of the decode workload reads only 42 prompt tokens. It lasts a few tens of milliseconds, which is
shorter than one power record. In the October probe, phases that short failed their prechecks in all 24 members. This
**short-prompt prefill** is therefore registered as **expected unresolvable**: its energy is computed if it can be,
it is never printed, and its failure stops nothing else (repository label `prefill-p42`).
<!-- src: registration §0.5 l.328-330; §0.9 l.442-443 -->

The **prefill workload** has a prompt of exactly 2,048 tokens and 512 output tokens (repository label
`prefill-p2048`). Its length is what the October probe was run to choose. The probe tried prompts of 512, 1,024, 2,048
and 4,096 tokens and selected the shortest one at which the prefill of every 1.7B-model member overlapped at least 5
power records.
<!-- src: registration §0.5 l.331-334; configs/campaigns/g2a_prefill_probe_25g83/registration_block3.md l.85 -->
<!-- calc: 1.7 restates the model name in the cited line -->

## 6. From members to numbers: repeats, quads, units and reported cells

One member is one draw from a process that varies. A number worth reporting needs repeated draws, and a comparison
between two conditions (a condition is one model on one workload) needs protection from **drift**: a slow change, over minutes to hours, in what the same work
costs or in what an instrument reads, from causes such as temperature and background activity.

An **absolute repeat** is one member run on its own, not paired with any other. The design runs ten in a row for each
model and workload.
<!-- src: registration §0.8 l.429 -->
<!-- calc: ten is the 10 of the cited line -->

A **quad** is four consecutive members in the order A1, B1, B2, A2, where A and B are two conditions. A and B are the
quad's two **sides** (the repository calls a quad a `block`).
<!-- src: registration §0.8 l.418-420 -->
<!-- calc: A1, B1, B2, A2 are labels, not values: 1, 2 -->

The order A, B, B, A is chosen because a steady drift cancels inside it. Worked example. Suppose every member reads
δ more than the member before it. The four positions then carry 0, δ, 2δ and 3δ of drift. Side A holds the first and
last positions and averages 1.5δ. Side B holds the two middle positions and also averages 1.5δ. The difference
between the sides gains nothing from the drift. A drift that curves does not cancel: with drift 0, 1, 4 and 9 at the
four positions, side A averages 4.5 and side B averages 2.5.
<!-- src: registration §0.8 l.421-424 -->
<!-- calc: (0 + 3)/2 = 1.5; (1 + 2)/2 = 1.5; squares of 0, 1, 2, 3 are 0, 1, 4, 9; (0 + 9)/2 = 4.5; (1 + 4)/2 = 2.5 -->

A **null quad** is a quad whose two sides are the same model and the same workload. Any difference between its sides
can only come from the instrument and the machine.
<!-- src: registration §0.8 l.425-426 -->

A quad's **quad difference** is d = (B1 + B2)/2 − (A1 + A2)/2, where each symbol stands for that member's phase
energy. A **contrast** is the mean of the quad differences, for one phase, over quads in which side A is the 1.7B
model and side B is the 8B model on the same workload. For example, with invented phase energies A1 = 10.0 J,
B1 = 13.1 J, B2 = 12.9 J and A2 = 10.2 J, the quad difference is 13.0 − 10.1 = 2.9 J.
<!-- src: registration §0.8 l.427-428 -->
<!-- synthetic: 10.0, 13.1, 12.9, 10.2; calc: (13.1 + 12.9)/2 = 13.0; (10.0 + 10.2)/2 = 10.1; 13.0 - 10.1 = 2.9; 1.7 and 8 are model names -->

A **unit** is a group of members that the statistics treat as one independent draw. Each absolute repeat is one unit,
and each quad is one unit. A **stratum** is one kind of unit: the repeat stratum or the quad stratum. Consecutive
units share slow drifts, so their independence is an assumption of the analysis, not a measured fact.
<!-- src: registration §0.8 l.430-434 -->

A **reported cell** is one registered energy number for one model and one phase. It is computed from that model's 10
absolute repeats and 10 null quads on the workload in question: 20 units, 50 members. The **paper cells** are the four
reported cells the paper prints: decode, and prefill at 2,048 tokens, for each of the two models (the repository also
calls them target cells). The short-prompt prefill has a reported cell for each model too, and by Section 5 it is
never printed.
<!-- src: registration §0.5 l.331; §0.8 l.432; §0.9 l.438-443 -->
<!-- calc: 10 + 10 = 20 units; 10 + 10 x 4 = 50 members -->

The number a reported cell prints is a mean of gross phase energies, and the analysis plan fixes its arithmetic. A
member can be lost (Section 3 met one, aborted by idle admission), so the arithmetic is written for the units that
remain. Let n_r be the number of absolute repeats that remain and n_b the number of null quads that remain, and reduce
each quad to one value, the mean of its four members' phase energies. The cell's mean is

    m = 0.2 × (mean of the n_r repeat energies) + 0.8 × (mean of the n_b quad means).
<!-- src: analysis plan §4 l.224-227 -->

The weights are 0.2 and 0.8 because 10 of the 50 planned members are repeats and 40 are members of quads. With all 20
units present, m equals the plain mean of the 50 members. With a unit missing, a plain mean over the remaining members
would shift weight from one stratum to the other, and the fixed weights prevent that.
<!-- src: analysis plan §4 l.221-227 -->
<!-- calc: 10/50 = 0.2; 40/50 = 0.8; four members to a quad -->

The scatter among the units sets how far m can be trusted. Let s_r be the sample standard deviation of the repeat
energies and s_b that of the quad means. The variance of m is

    V = 0.04 × s_r² / n_r + 0.64 × s_b² / n_b,
<!-- src: analysis plan §4 l.228-229 -->

and the cell's **half-width** is t × √V, where t is the 97.5th percentile of Student's t distribution with
min(n_r, n_b) − 1 degrees of freedom. The range from m minus the half-width to m plus the half-width is a 95%
confidence interval for the cell's mean if the units are independent draws. It is a cautious one, because t takes its
degrees of freedom from the smaller stratum. Independence is the assumption named above, so every half-width the
paper prints carries that caveat. The half-width accounts for the scatter among the units of one measurement session
and for nothing else: not for error in timing, which Sections 8 and 9 add to it, and not for differences between one
session and another.
<!-- src: analysis plan §4 l.228-232, 278-280 -->
<!-- calc: 0.2 squared is 0.04; 0.8 squared is 0.64; the 97.5th percentile leaves 2.5% in each tail, 5% in all, hence 95%; min(n_r, n_b) - 1 uses 1 -->

Worked example, with the analysis plan's invented values. Ten repeats read 10.0, 10.2, 9.9, 10.1, 10.0, 10.3, 9.8,
10.1, 10.0 and 9.6 J: their mean is 10.0 J and s_r = 0.2 J. Ten quad means are 10.4, 10.1, 10.3, 10.2, 10.5, 10.0,
10.2, 10.3, 10.1 and 9.9 J: their mean is 10.2 J and s_b = 0.18257 J. Then m = 0.2 × 10.0 + 0.8 × 10.2 = 10.16 J and
V = 0.04 × 0.04 / 10 + 0.64 × 0.033333 / 10 = 0.0022933 J², whose square root is 0.047889 J. For 9 degrees of freedom
t = 2.262157, so the half-width is 2.262157 × 0.047889 = 0.10833 J. Now suppose repeat 6 (10.3 J) and quads 5 and 9
(10.5 and 10.1 J) are lost, so that n_r = 9 and n_b = 8. Then m = 0.2 × 9.96667 + 0.8 × 10.175 = 10.13333 J,
V = 0.0023730 J², t takes 7 degrees of freedom and is 2.364624, and the half-width is 2.364624 × 0.048714 = 0.11519 J.
<!-- src: analysis plan §4 l.230-231, 259-271 -->
<!-- calc: 0.2 squared is 0.04; 0.18257 squared is 0.033333; 10 - 1 = 9; min(9, 8) - 1 = 7; the square root of 0.0023730 is 0.048714 -->

## 7. Running members in order: stages, the chain, packs and windows

A **stage** is an ordered list of members that one invocation of the measuring program runs one after another
(repository file `scripts/run_campaign.py`).
<!-- src: registration §0.6 l.342 -->

A **settle** is a wait of 60 s at the start of every stage, during which nothing runs, so that the machine is back at
idle before the stage's first member. 60 s is enough because processor power is back at idle within about 15 s after
a decode ends.
<!-- src: registration §0.6 l.343, 346-347 -->

A **cooldown** is the wait between two members of the same stage. During it the measuring program takes readings of
the idle machine. Each reading is a short recording by the sampler, of 50 power records and about 6.5 s, reduced to
its mean processor power. The next member starts at the first reading whose mean is at most twice the mean of the
previous member's idle baseline, provided the operating system reports its thermal state as nominal. If no reading
meets that rule, the next member starts anyway when the cooldown has lasted 300 s, its **cap**. A member that started
at the cap is recorded as having done so and is taken out of every number, because no reading had met the rule
before it began. The first member of a stage has no previous member and no cooldown.
<!-- src: registration §0.6 l.350-355; §5.5 l.1870-1871; §6.3 l.2170-2171 -->

Worked example, with one real and two invented values. The previous member's idle baseline averaged 0.037 W, the
October probe's median, so the limit is twice that, 0.074 W. The first reading averages 0.082 W, which is above the
limit: no start. The second averages 0.045 W with the thermal state nominal: the next member starts at that reading.
<!-- src: registration §0.6 l.359-361 -->
<!-- calc: 2 x 0.037 = 0.074 -->

A **pack** is the complete plan of one measurement session: its stages in order, the configuration of every member,
and the planned counts, every file of it pinned.
<!-- src: registration §0.7 l.388-390 -->

The **chain** is the script that runs a pack's stages in order.
<!-- src: registration §0.6 l.343; §0.17 l.803 -->

An **attempt** is one try at running one pack from beginning to end. Its **scheduled start** is the instant, fixed in
advance, at which the operating system launches it. A **window** is the stretch of machine time an attempt occupies,
from its scheduled start to the moment its chain exits.
<!-- src: registration §0.7 l.409-411; §0.17 l.797-798 -->

A **science member** is a member whose phase energy feeds a reported cell or a contrast. The other members of a
window exist to watch the instrument; Section 9 builds them.

There are three packs, and the paper names each pack's window after what it holds.

- The **1.7B window** (repository label: ALPHA) holds, for the 1.7B model, the 10 absolute repeats and 10 null quads
  of the decode workload and the same for the prefill workload: 100 science members.
- The **8B window** (repository label: BETA) holds the same for the 8B model.
- The **contrast window** (repository label: GAMMA) holds 10 quads for each workload in which side A is the 1.7B model
  and side B is the 8B model: 80 science members, the source of the paper's two contrasts.
<!-- src: registration §0.7 l.392-394; §0.9 l.438-443; §0.12 l.493-494 -->
<!-- calc: 2 workloads x 50 members = 100; 2 workloads x 10 quads x 4 members = 80; 1.7 and 8 are model names -->

The 1.7B window and the 8B window are together the **single-model windows** (the repository calls their packs the
floor packs).
<!-- calc: 1.7 and 8 are model names -->

A window can start at any hour, and windows run back to back, several to a day: the next window is scheduled as soon
as the files of the one before it have been archived and processed. The registration has two planning figures for how
long a chain takes: a slower one built from member timings measured in the October probe, and a faster one that
subtracts the time saved by changes made since. On the faster figure the three chains take 5.4 h (1.7B window), 5.7 h
(8B window) and 4.8 h (contrast window), 15.9 h in all. On the slower they take 8.8, 9.1 and 7.7 h, 25.6 h in all.
Each chain has work before it and after it. Before the chain, the checks that decide whether it may start take between
4 and 46 minutes (Section 11). After it, archiving and processing the window's files and scheduling the next window
take 0.6 to 1.6 h. If each pack needs only one attempt, the three windows together therefore take between
15.9 + 3 × 0.6 + 3 × 0.07 = 17.9 h and 15.9 + 3 × 1.6 + 3 × 0.77 = 23.0 h on the faster figure, and between 27.6 and
32.7 h on the slower: about 18 to 23 h, or 28 to 33 h. That is one window every 6 to 8 h on the faster figure and
every 9 to 11 h on the slower, so all three windows fit inside one day on the faster figure and inside a day and a
half on the slower. The first window measures which figure is right. A pack that needs a second attempt adds one more
window of about its own length. (Some file and directory names in the repository say "night". The word is a leftover
and implies no time of day.)
<!-- src: registration §5.5 l.1848-1852, 1877-1890, 1898-1908; §7.2 l.2791-2796; §7.3 l.2845 -->
<!-- calc: 5.4 + 5.7 + 4.8 = 15.9; 8.8 + 9.1 + 7.7 = 25.6; 4 minutes = 0.07 h and 46 minutes = 0.77 h (the 46 is derived with the dwell in Section 11; the registration prints 47); 3 x 0.6 = 1.8; 3 x 0.07 = 0.2; 15.9 + 1.8 + 0.2 = 17.9; 3 x 1.6 = 4.8; 3 x 0.77 = 2.3; 15.9 + 4.8 + 2.3 = 23.0; 25.6 + 1.8 + 0.2 = 27.6; 25.6 + 4.8 + 2.3 = 32.7; 17.9 / 3 = 6.0; 23.0 / 3 = 7.7, about 8; 27.6 / 3 = 9.2, about 9; 32.7 / 3 = 10.9, about 11; three windows; 1.7 and 8 are model names -->

A **measurement block** is a set of windows registered and sealed under one registration. The three windows above
form the measurement block this paper reports (repository label: measurement block 5).
<!-- src: registration §0.7 l.412-413 -->
<!-- calc: three windows, as listed above; 5 is the label in the cited line -->

## 8. Time: placing power records against phase edges

Phase energy depends on where each power record sits in time relative to the phase edges, and the two are timed by
different means. Each power record carries a label printed by the sampler: the calendar second in which the record
ended, and the record's duration. Each phase edge is stamped by the measuring program: the program records the
reading of the machine's clocks at that instant.
Placing the records against the edges therefore needs the offset between the two ways of telling time, and an error
in that offset moves energy across a phase edge. For scale, an error of 5 ms while the processor draws 40 W moves at
most 0.005 s × 40 W = 0.2 J across one edge.
<!-- src: registration §0.14 l.720-723 -->
<!-- calc: 5 ms = 0.005 s; 0.005 x 40 = 0.2 -->

The machine has two kinds of clock. The **wall clock** tells the time of day, and the operating system may adjust it
(repository label: CLOCK_REALTIME). A **monotonic clock** is a counter that only moves forward and that nothing sets.
The measuring program stamps its events on one monotonic clock (Python's `time.monotonic_ns`). The clock
measurements made before and during a window (Section 11) use another, the **raw monotonic clock** (repository
label: CLOCK_MONOTONIC_RAW). The two differ by a constant unless the machine sleeps. The **clock anchor** is the wall
clock's reading minus the raw monotonic clock's reading, taken together in one process. If the wall clock is moved,
the clock anchor moves by the same amount at once.
<!-- src: registration §0.14 l.732-733; §0.17 l.828-830; §5.8 l.2058-2059 -->

**Network time** is the operating system's automatic setting of the wall clock from a time server. The **frequency
word**, written f, is the correction the operating system's kernel currently applies to the rate of the wall clock,
in parts per million (ppm). The design switches network time off before every window. With network time off, nothing
moves the wall clock suddenly, and the clock anchor changes steadily at the rate f. On 2026-10-05 f was −3.17 ppm, at
which the clock anchor moves about 0.27 s per day.
<!-- src: registration §0.14 l.734-737; §4.4 l.1361-1362 -->

A **clock step** is a sudden move of the wall clock, as opposed to that steady change. The **residual** is the change
in the clock anchor since some starting instant, minus f multiplied by the time elapsed on the raw monotonic clock.
Steady change leaves the residual flat. A clock step makes it jump, and a jump of more than 1 ms between two
consecutive readings of the clock anchor is what the paper's programs count as a clock step.
<!-- src: registration §0.14 l.738-739; §4.2 l.1207-1208 -->

The **member clock bound** is an upper limit, computed for each member from its own sampler stream, on the error in
placing that member's power records on the clocks that stamped its phase edges (repository label: effective
bound). It is the sum of three parts.

The first part comes from the labels on the records. The method assumes that over one sampler stream the wall clock
is a straight-line function of the monotonic clock: one offset and one constant rate, with no clock step. Each
record's end, found by adding up the durations of the records up to it, must then fall inside the calendar second
printed on it. That second is widened by 250 µs at each end, a fixed allowance for how far the sampler's label may
depart from the straight line. A pair of offset and rate that satisfies every record at once is called an admitted
pair here, and the set of all admitted pairs is computed exactly. Each admitted pair puts the end of the first record
at one wall-clock time. The first part, called h, is half the range of those times: the latest minus the earliest,
halved.
<!-- src: registration §0.14 l.725-728; joulewise/uncertainty_evidence.py l.42, 891-897, 1269-1270, 1311 -->

The second part is measured. At five instants, from before it starts the sampler to after it has read the sampler's
last record, the measuring program reads the wall clock between two readings of the monotonic clock, which confines
the difference between the two clocks at that instant to a narrow range. The second part is the largest difference
any of the five ranges allows minus the smallest: how far the wall clock moved against the monotonic clock over the
stream. The third part is about 2 µs: the resolution of the clock readings plus 1 µs for rounding.
<!-- src: registration §0.14 l.728-730; joulewise/uncertainty_evidence.py l.103, 111-117, 354-373, 1090, 1311-1326 -->
<!-- calc: the padding 1e-6 s in the cited code line is 1 µs; three parts and five instants are counts of the cited lines -->

A member is **bounded** when this computation can be made and the member clock bound is at most 5 ms. The
computation can be made only if all of the following hold. The records after the first add up to at least 60 s, and
the measuring program's own monotonic clock readings, from before it started the sampler to after it read the last
record, span at least as long. The calendar second printed on the records changes at least twice within the stream.
Every rate among the admitted pairs is within 50 ppm of the monotonic clock's rate. The measuring program first read
the sampler's output no earlier than the end of the first record and no more than 0.25 s after it. And the records
are consistent with themselves: every printed label is a whole second, the labels never run backwards and never jump
ahead by more than a record's duration plus one second, and the energy the sampler prints for each record agrees with
that record's power multiplied by its duration, to within 0.002 J plus a thousandth of the energy (repository file
`joulewise/uncertainty_evidence.py`). A member that is not bounded is removed from every number.
<!-- src: registration §0.14 l.730-731; joulewise/uncertainty_evidence.py l.39-47, 108-110, 1001-1088, 1255-1293 -->
<!-- calc: "at least twice" is the 2 of the cited code line; a thousandth is the 0.001 of the cited code line -->

Worked example. Take h = 3.6 ms, the largest h any member showed in the October probe; a sampler stream of 300 s;
and f = −3.17 ppm. The second part is measured in a real member, but with network time off it can be predicted: the
wall clock moves against the monotonic clock at the rate f, so over a stream of length T the second part is about
|f| × T. Here that is 3.17 millionths of 300 s, which is 0.951 ms. The member clock bound is
3.6 + 0.951 + 0.002 = 4.553 ms. That is at most 5 ms, so the member is bounded.
<!-- src: registration §0.14 l.729-731, 736-737; §4.2 l.1200 -->
<!-- synthetic: the 300 s stream is invented; calc: 3.17e-6 x 300 s = 0.000951 s = 0.951 ms; 2 µs = 0.002 ms; 3.6 + 0.951 + 0.002 = 4.553 -->

The example shows that the second part grows with the size of f and with the length of the sampler stream. The
**longest stream** any member of the measurement block can have is 335 s: a member of the 8B model that needed its
idle baseline recorded twice, followed by its warm-up and its measured request, with the margins the registration's
sizing adds around them (repository label: T_stream_max).
<!-- src: registration §0.14 l.740-744 -->
<!-- calc: 8 is the model name -->

The **frequency gate** is the test, made before a window starts, that predicts the largest member clock bound the
window could produce and refuses the window if that prediction exceeds 5 ms. The prediction is
3.7 ms + (|f| + 0.25 ppm) × 335 s. Its three numbers are built as follows: 3.7 ms is the October probe's largest h,
3.6 ms, plus a margin of 0.1 ms; 0.25 ppm allows for the wall clock's rate over one stream differing from the
frequency word; and 335 s is the longest stream. One part per million of 335 s is 0.335 ms. Worked example: at
f = −3.17 ppm the prediction is 3.7 + 3.42 × 0.335 = 4.846 ms, which passes. At |f| = 3.7 ppm it is
3.7 + 3.95 × 0.335 = 5.023 ms, which refuses. The frequency gate passes for any |f| up to 3.6306 ppm.
<!-- src: registration §0.14 l.745-746; §4.2 l.1199-1204 -->
<!-- calc: 335 s x 1e-6 = 0.335 ms; 3.17 + 0.25 = 3.42; 3.7 + 0.25 = 3.95 -->

The member clock bound covers the alignment of two clocks. A second timing question is how faithfully the power
records show the instant at which power actually changed. That is measured with a known signal.

A **pulse calibration** is a recording in which a program switches a load on the GPU on and off 59 times, noting the
instant of each command, while the sampler runs. Each on-and-off pair is one pulse. For each pulse an estimator fits
the power records as a resting level plus a rectangle whose start and end may each be delayed from the commanded
instants, and returns the range of delays that the records are consistent with. The **pulse timing bound** of the
recording is the largest delay, in absolute value, at either end of any of those ranges: the largest timing error
between a commanded edge and the edge the power records show (repository label: fiducial bound). With 59 pulses it is
a bound that holds for at least 95% of pulses with 95% confidence, treating the pulses as independent draws: if more
than 5% of pulses could exceed it, the chance that all 59 stayed below it would be less than 0.95 multiplied by itself
59 times, which is 0.0485, and that is below 0.05.
<!-- src: registration §0.11 l.458-462 -->
<!-- calc: 0.95^59 = 0.0485; 5% = 100% - 95% = 0.05 -->

Each window is enclosed by two pulse calibrations: the **pre calibration**, before its first member, and the **post
calibration**, after its last. Together they are the window's **bracket**.
<!-- src: registration §0.11 l.463 -->

The **calibration acceptance** is the pinned file that holds the limits a bracket must meet on this
operating-system build. It was derived from 24 pulse calibrations recorded before the measurement block, and it
fixes three numbers. The **pre screen**,
0.036462861644980 s, is the largest pulse timing bound among those 24; a pre calibration whose bound is above it
stops the chain before any member runs. The **bracket screen**, 0.014531 s, is the range of the 24 bounds, their
largest minus their smallest. The third number is a limit, 0.01550217418713139 s, on the quantity built next.
<!-- src: registration §0.11 l.464-469 -->
<!-- calc: three numbers are the three named in the cited lines -->

A pulse calibration measures the edge timing only at the time it is recorded, and a window lasts hours. If that
timing moved in between, members in the middle of the window had their power records lined up against their phase
edges with a larger error than either calibration measured, and energy was credited to the wrong phase with nothing
to show it. The **bracket drift allowance** of a window is the amount set aside for such movement. It is added to the
larger of the window's pre and post pulse timing bounds, and the sum is the limit on edge-timing error that the
analysis applies to the whole window (Sections 9 and 10 use it). The allowance is the larger of two values: the
absolute difference between the window's post and pre bounds, and the bracket screen. It is never smaller than the
bracket screen because the 24 earlier bounds differed by that much among themselves, so two bounds that happen to
agree are no evidence that the timing stood still between them. The allowance must not exceed
0.01550217418713139 s; if it does, the bracket fails. That limit is the calibration acceptance's 99% prediction limit
for the difference between two pulse timing bounds from one recording session: √2 × t × s_w, where s_w is the
standard deviation of the 24 bounds about the mean of the session each was recorded in (they were recorded in 2
sessions) and t is the 99.5th percentile of Student's t distribution with 24 − 2 = 22 degrees of freedom. A
difference beyond it is read as the edge timing having changed during the window.
<!-- src: registration §0.11 l.464-469; configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json l.1092-1102; scripts/issue_calibration_acceptance_generation.py l.2304-2340; joulewise/calibration_bracketing.py l.1221-1224 -->
<!-- calc: a 99% two-sided limit leaves 0.5% in each tail, hence the 99.5th percentile; 24 - 2 = 22 -->

Worked example, with invented bounds. A pre calibration gives 0.0281 s, which is below the pre screen, so the chain
goes on. The post calibration gives 0.0304 s. The difference is 0.0023 s; the bracket drift allowance is the larger of
0.0023 s and 0.014531 s, that is 0.014531 s, which does not exceed 0.01550217418713139 s: the bracket passes. Had the
post calibration given 0.0440 s, the difference would be 0.0159 s, the allowance 0.0159 s, and the bracket would
fail.
<!-- src: registration §0.11 l.467-469 -->
<!-- synthetic: 0.0281, 0.0304, 0.0440; calc: 0.0304 - 0.0281 = 0.0023; 0.0440 - 0.0281 = 0.0159 -->

The **calibration ledger** is the file, only ever appended to, that records every pulse calibration taken on the
machine. Before a window's pre calibration the chain makes the **bracket reservation**: it opens an entry in the
calibration ledger that names the window's plan, and the pre and post calibrations are then recorded against that
entry (repository label: bracket session). Because the entry exists before either calibration runs, every
calibration taken for a window is on record whatever it shows: one that came out badly cannot be left out, and none
can be attached to a window after its bound is known.
<!-- src: registration §0.11 l.470-477; docs/contracts/calibration_ledger.md l.5-11 -->

The **attribution floor** is an estimate, about 1 J, of how much energy can be credited to the wrong phase because a
phase edge is located only to within the sampler's timing error. For scale, an edge misplaced by 0.030 s while the
processor draws 33 W moves 0.030 × 33 ≈ 1 J from one phase to its neighbour. The attribution floor is printed beside
each reported cell as a number of its own and is added into no other number. At this writing the registration has not
yet fixed its exact value for this operating-system build.
<!-- src: registration §0.10 l.451-454 -->
<!-- synthetic: 0.030 s and 33 W are an invented illustration; calc: 0.030 x 33 = 0.99 -->
<!-- open at this writing: the registration's unfilled value ATTRIBUTION-FLOOR-BINDING, §0.10 l.453-454 and §14 Q5 -->

## 9. Drift across a window: reference members

A quad cancels steady drift across its four members. It does not show how far the machine drifted over the hours of
a whole window, and an absolute repeat, which is paired with nothing, has no protection from drift at all. Drift over
a window is therefore measured directly, by running one unchanging job at the window's start, middle and end.

The **reference workload** is that job: a third model, Qwen2.5-1.5B, with a prompt of 1,024 tokens and 256 output
tokens. A **reference member** is a member that runs the reference workload. Its energy is never part of a reported
cell or a contrast.
<!-- src: registration §0.12 l.489-490, 695 -->
<!-- calc: 2.5 and 1.5 are parts of the model name Qwen2.5-1.5B -->

Each window runs reference members at four places. The **reference corpus** is the 12 reference members run before
any science member (repository label: NEG-8 corpus; the label is an inherited name, not an abbreviation). The
**start triplet** is three more, run next. The **midpoint reference** is one, run halfway through the science
members, where the members of the decode workload end and those of the prefill workload begin: after science member
50 of 100 in a single-model window and after science member 40 of 80 in the contrast window. The **end triplet** is
three, run after the last science member. The start triplet, the midpoint reference
and the end triplet are the window's three **reference stages**.
<!-- src: registration §0.12 l.489-495 -->
<!-- calc: four places are the corpus and the three reference stages; three stages are counted from the cited lines -->

The contrast window also runs two **interior references**: one reference member in the middle of each of its halves
(the decode workload's members, then the prefill workload's), after science members 20 and 60. They are recorded as a
measure of drift inside each half, and neither of the two computations below reads them.
<!-- src: registration §0.12 l.503-507 -->
<!-- calc: two interior references, at members 20 and 60 -->

A **lost reference** is a reference member whose energy cannot be trusted for a reason that has nothing to do with
the energy's value: it never ran or left no bundle; it did not finish successfully, for example because idle
admission aborted it; its summary cannot be read, or its bundle fails the checks every bundle must pass (its files
are present, unaltered and tied to the planned configuration); a physical disturbance was recorded during it, such as
a competing process, battery charging, thermal pressure or a clock step; or the record of which model it ran is
missing or names another model. The test for a lost reference never reads the reference member's energy, so none can
be dropped for its value. A **surviving reference** is a reference member of a reference stage that is not a lost
reference.
<!-- src: registration §0.12 l.535-545, 566-570, 598-599 -->

A **spare** is an extra reference member, planned and pinned in advance, that runs only when a reference stage ended
with fewer successful members than planned. Each triplet has three spares and the midpoint reference has one. A
reference stage gets one retry, which runs as many spares as members were missing, and a spare that runs takes the
missing member's place. A retry is never run because of an energy value.
<!-- src: registration §0.12 l.496-498, 601-611 -->
<!-- calc: three spares and one spare are the counts of the cited lines -->

The **reference drift bound** is the largest difference between a start mean and an end mean that the reference
corpus itself could produce when nothing drifts (repository label: NEG-8 bound). Let n be the number of reference
corpus members kept: 12, or 10 or 11 when one or two did not finish successfully or were dropped for a recorded
physical disturbance. With fewer than 10 no bound is derived and the window supports no claim. The energy of a
reference member, here and below, is the gross energy of its whole measured request. Let s be the sample standard
deviation of the kept members' energies, and t the 97.5th percentile of Student's t distribution with n − 1
degrees of freedom. Let U_j be the mean of the j largest of those energies and L_j the mean of the j smallest. For
n_s surviving references in the start triplet and n_e in the end triplet,
<!-- src: registration §0.12 l.511-516; §5.3 l.1639-1644, 1670 -->
<!-- calc: n - 1 uses 1; one or two dropped members: 12 - 11 = 1, 12 - 10 = 2 -->

    bound(n_s, n_e) = max( max(U_ns − L_ne, U_ne − L_ns),  t × s × √(1/n_s + 1/n_e) ).
<!-- src: registration §0.12 l.516 -->

The first term is the widest gap that a start mean of n_s members and an end mean of n_e members could show if both
were drawn from the reference corpus. The second term is the 95% repeatability limit for the difference of two such
means when nothing drifts.
<!-- src: registration §0.12 l.518-522 -->

The **reference drift check** asks whether the window drifted more than that (repository label: NEG-8 screen). It
passes when the absolute difference between the mean of the surviving references of the end triplet and the mean of
the surviving references of the start triplet is at most bound(n_s, n_e). It is applied a second time with every
energy, in the bound and in the means, replaced by the reference member's idle-subtracted energy, and both
applications must pass. It needs at least 2 surviving references in each triplet. A window that fails the reference
drift check, or cannot run it, supports no claim.
<!-- src: registration §0.12 l.511-512, 527-528, 615-617; joulewise/whole_window.py l.1604-1616 -->

The **spread** of a window is the largest minus the smallest of three values: the start mean, the midpoint
reference's energy, and the end mean. When the midpoint reference is a lost reference, the spread is the absolute
difference of the two means. The **whole-window drift allowance** is the larger of the spread and bound(n_s, n_e). It
is the amount by which drift may have moved energies measured at different times in the window. Each member's energy
is given half of it as a bound, so that a difference between two members carries it once.
<!-- src: registration §0.12 l.529-534 -->
<!-- calc: three values are the three named; two means are the start and end means -->

Worked example, with invented energies (the twelve corpus values and their bound are the registration's own example).
The reference corpus reads, in joules: 99.62, 99.71, 99.80, 99.88, 99.93, 99.97, 100.04, 100.09, 100.15, 100.22,
100.31 and 100.38. Then s = 0.2353 J and, for 11 degrees of freedom, t = 2.201. The three largest average
U_3 = 100.3033 J and the three smallest average L_3 = 99.7100 J. With three surviving references in each triplet,
bound(3, 3) = max(100.3033 − 99.7100, 2.201 × 0.2353 × √(2/3)) = max(0.5933, 0.4228) = 0.5933 J. Suppose the start
triplet reads 100.02, 99.91 and 99.95 J, a mean of 99.96 J; the midpoint reference reads 100.20 J; and the end
triplet reads 100.26, 100.19 and 100.21 J, a mean of 100.22 J. The reference drift check compares
100.22 − 99.96 = 0.26 J with 0.5933 J and passes. The spread is also 0.26 J, because the midpoint reference lies
between the two means. The whole-window drift allowance is the larger of 0.26 J and 0.5933 J, that is 0.5933 J, and
each member carries 0.2967 J.
<!-- src: registration §0.12 l.670-676 -->
<!-- synthetic: end triplet 100.26, 100.19, 100.21 and the means 99.96 and 100.22; calc: 12 - 1 = 11; 1/3 + 1/3 = 2/3; 100.22 - 99.96 = 0.26; 0.5933 / 2 = 0.2967 -->

Every limit on timing is now built, and the reported cell of Section 6 can be given its full range. The half-width
covers the scatter among units. It cannot cover a timing error that the units share, because an error that shifts
every unit alike leaves no trace in their scatter. Two bounds, in joules, are added for that.

The first is the **timing uncertainty** of a member's phase energy: the largest amount by which that phase energy
changes when the timing behind it is moved as far as its limits allow. The reducer tries every allowed movement and
keeps the largest change. All the member's power records are shifted together, earlier or later, by any amount up to
the member clock bound. At the same time each of the two phase edges is moved on its own, earlier or later, by up to
the window's limit on edge-timing error (Section 8: the larger pulse timing bound of the bracket plus the bracket
drift allowance), to which the second part of the member clock bound is added. The second bound is half the
whole-window drift allowance of the member's window, the allowance being the one computed from gross energies. (The
analysis plan sums a third recorded bound, for instruments that report power at instants and must interpolate
between them. It is zero here, because every record of this sampler carries its own support interval.)
<!-- src: analysis plan §4 l.233-237, 245-246; joulewise/reduce.py l.541-555, 2148-2162, 2219-2224; joulewise/whole_window.py l.855-866 -->
<!-- calc: two bounds and two phase edges are counts -->

For each of the two bounds take 0.2 × its mean over the repeats that remain plus 0.8 × its mean over the members of
the quads that remain, the same weights as for m, and call the sum of the two results B. The cell's **reported interval** runs
from m minus the half-width minus B to m plus the half-width plus B. In the example of Section 6, if the two weighted
means are 0.010 J and 0.050 J, then B = 0.060 J and the reported interval runs from
10.16 − 0.10833 − 0.060 = 9.9917 J to 10.16 + 0.10833 + 0.060 = 10.3283 J. The reported interval covers the scatter
among the units of one window and these timing bounds. It does not cover differences between windows. The attribution
floor of Section 8 is not part of B: it is printed beside the reported interval and never added into it.
<!-- src: analysis plan §4 l.244-247, 255-263, 278-280 -->
<!-- synthetic: 0.010 and 0.050 are the analysis plan's invented values; calc: 0.010 + 0.050 = 0.060; 10.16 - 0.10833 - 0.060 = 9.9917; 10.16 + 0.10833 + 0.060 = 10.3283; two bounds -->

## 10. Floors, ratios, and how strong a claim may be

The **detection floor** of one model and phase is the largest difference the instrument and the machine produce when
nothing differs; hence the smallest real difference the measurement can tell apart from none. It is estimated in two
forms. The **absolute form** uses the model's absolute repeats: how far single members of identical work scatter
around their mean. The **comparative form** uses its null quads: how large a quad difference appears when the two
sides are the same. A contrast whose estimate does not exceed its detection floor is reported as **not resolvable**,
never as a difference and never as the absence of one.
<!-- src: registration §0.10 l.447-450; analysis plan §5 l.284-287; docs/contracts/claims_ladder.md l.47-48 -->

Both forms apply one rule to n values. In the absolute form the values are the phase energies of the absolute
repeats that remain, and each value's deviation is its distance from the mean of the n values. In the comparative
form the values are the quad differences of the null quads that remain, and each value's deviation is the quad
difference itself: it is not measured from the mean, because with identical sides the true difference is zero. Let s
be the sample standard deviation of the n values and t the 97.5th percentile of Student's t distribution with n − 1
degrees of freedom. The prediction term is t × s × √(1 + 1/n) in the absolute form, and the absolute value of the
mean quad difference plus t × s × √(1 + 1/n) in the comparative form. The detection floor at the recorded values is
the larger of two numbers: the largest deviation, in absolute value, and the prediction term.
<!-- src: analysis plan §5 l.295-300 -->
<!-- calc: n - 1 uses 1; 1 + 1/n uses 1 -->

That floor takes every value as recorded, but each value could be wrong, through timing alone, by up to some amount
w in either direction. For an absolute repeat, w is the timing uncertainty of the member's phase energy (Section 9).
For a null quad's difference, w is the sum of a shared part and a local part. For the shared part, the start of the phase is moved by
one common amount in all four members, anywhere from −b to +b, and the quad difference is recomputed along the way;
the same is done with the end of the phase. Here b is the window's limit on edge-timing error (Section 8). With z the
quad difference when nothing is moved, the shared part is the larger of |(lowest value while the start moves − z) +
(lowest value while the end moves − z)| and the same expression with the highest values, plus |z − d|, where d is the
quad difference as recorded. The local part is half the sum, over the four members, of the timing uncertainty each
member's phase energy would have if the window's limit on edge-timing error were zero, which leaves only the
member's own clock error. Each value may then lie anywhere from w below to w above its recorded value. The floor is
recomputed for every combination in which each value sits at one end of its range or the other, 2ⁿ combinations,
and the largest result is kept; it is never taken smaller than the floor at the recorded values. The detection floor
that is printed and used is this widened value. When fewer than 10 values remain it is also multiplied by a guard
factor, a fixed safety margin for the smaller sample, of √(9/(n − 1)): 1.0607 at n = 9 and 1.1339 at n = 8.
<!-- src: analysis plan §5 l.301-316; joulewise/floor_extraction.py l.2478-2494 -->
<!-- calc: 2 to the power n; four members to a quad; n - 1 uses 1 -->

Worked example of the absolute form, with the ten invented repeat energies of Section 6: 10.0, 10.2, 9.9, 10.1, 10.0,
10.3, 9.8, 10.1, 10.0 and 9.6 J. Their mean is 10.0 J, s = 0.2 J, and the largest deviation is 0.4 J, that of the
last value. With n = 10 and t = 2.262 for 9 degrees of freedom the prediction term is 2.262 × 0.2 × √1.1 = 0.4745 J.
The larger of 0.4 and 0.4745 is 0.4745 J, the detection floor at the recorded values. Now give every repeat
w = 0.05 J. Among the 1,024 combinations the largest floor is 0.5730 J. One combination that reaches it is 9.95,
10.25, 9.85, 10.15, 9.95, 10.35, 9.75, 10.15, 10.05 and 9.55 J, for which s = 0.24152 J and the prediction term is
2.262 × 0.24152 × √1.1 = 0.5730 J. Ten values remain, so there is no guard factor.
<!-- src: analysis plan §4 l.259-260; §5 l.295-309, 320-321 -->
<!-- calc: ten is 10; 1 + 1/10 = 1.1; 10 - 1 = 9; 2 to the power 10 is 1,024; each value moved by 0.05 gives 9.95, 10.25, 9.85, 10.15, 9.95, 10.35, 9.75, 10.15, 10.05, 9.55, whose sample standard deviation is 0.24152 -->

Worked example of the comparative form, with the analysis plan's invented values. Ten null-quad differences are
0.10, −0.05, 0.20, 0.00, −0.10, 0.05, 0.15, −0.05, 0.10 and 0.00 J. Their mean is 0.04 J, s = 0.0966 J, and the
largest in absolute value is 0.20 J. The prediction term is 0.04 + 2.262 × 0.0966 × √1.1 = 0.2692 J, which is the
larger of the two, so the detection floor at the recorded values is 0.2692 J. With w = 0.30 J on every quad
difference, the largest floor among the 1,024 combinations is 1.0349 J.
<!-- src: analysis plan §5 l.297-300, 324-326 -->
<!-- calc: ten is 10; 1 + 1/10 = 1.1; 2 to the power 10 is 1,024 -->

The **dominance ratio**, written R, answers one question: is timing the part of the detection floor that limits the
measurement? It is the widened floor divided by the floor at the recorded values, both taken before any guard factor.
R of 2 or more means that timing error at least doubles the detection floor. In the two examples
R = 0.5730 ÷ 0.4745 = 1.21 and R = 1.0349 ÷ 0.2692 = 3.84. The registration uses R for one decision: the paper may
say that timing is what limits its measurement only if every registered dominance ratio is at least 2, and otherwise
each ratio that falls short is reported as it is.
<!-- src: registration §1 l.872-875; analysis plan §6 l.341-348, 357-358 -->

A **measurement stack** is everything that produced a number, taken together: the machine, the operating-system
build, the model runtime, the model, its quantization and the sampler.
<!-- src: registration §0.19 l.859-860 -->

The **claims ladder** is the project's fixed rule for how strong a claim may be (repository file
`docs/contracts/claims_ladder.md`). Two of its rungs matter here. An **instrument result** says: on this exact
measurement stack and measurement boundary, this quantity was observed (repository label: L1). A **comparative
result** says: one condition differed from another inside one measurement boundary, with intervals reported, the two
conditions alternated in time, and the difference above the detection floor (repository label: L2). The two higher
rungs, a fitted model checked on data held back from the fit and a repetition on other machines, are out of reach of
this design.
<!-- src: registration §0.19 l.859-863 -->
<!-- calc: two rungs here, two higher rungs, counted from the cited lines -->

Each single-model window can support instrument results: the phase energy of its model for decode and for prefill at
2,048 tokens. Printing the two models' reported cells next to each other is still two instrument results, because the
two windows ran one after the other and the models were never alternated. The contrast window, judged against
detection floors from both single-model windows, can support two comparative results, the 8B model's phase energy
minus the 1.7B model's for decode and for prefill at 2,048 tokens, and only when every registered condition for a
comparative result holds. Otherwise its wording stays that of an instrument result.
<!-- src: registration §0.5 l.331; §1 l.877-883; analysis plan §7.2 l.432-435 -->
<!-- calc: two instrument results and two comparative results are counted from the cited table; 8 and 1.7 are model names -->

The **Holm correction** keeps the chance of any false positive across the paper's two contrasts at 5%. Each contrast
has a p-value from its test. The smaller p-value is doubled; the larger is replaced by the greater of itself and that
doubled value; a contrast passes the Holm correction only when its adjusted value is at most 0.05. Worked
example, with invented p-values. With 0.012 and 0.030, the adjusted values are 0.024 and 0.030, and both contrasts
pass. With 0.030 and 0.040, the adjusted values are 0.060 and 0.060, and neither passes.
<!-- src: registration §0.19 l.864; analysis plan §7.1 l.399-401 -->
<!-- synthetic: 0.012, 0.030, 0.040; calc: 5% = 0.05; 2 x 0.012 = 0.024; max(0.024, 0.030) = 0.030; 2 x 0.030 = 0.060; max(0.060, 0.040) = 0.060; two contrasts -->

## 11. Starting a window: physical hazards and the arm

The design keeps a window's chain from starting for a short list of reasons, fixed in advance. Three kinds of
reason are decided by a sequence of checks made at the scheduled start: a physical condition of the machine, measured
directly, that would corrupt the energies; an agent session running on the machine; and a machine whose
operating-system build or model the calibration acceptance does not cover. Three narrower cases concern the launch
itself, and this section gives them once those checks are built. Every other problem is recorded and judged after
collection, which is the subject of Section 12.
<!-- src: registration preamble l.27-36; §0.15 l.758-766; §0.17 l.810-817 -->
<!-- calc: three kinds and three cases are counted from the cited lines and from joulewise/b5/driver.py l.88-93 -->

The **driver** is the program that the operating system's job scheduler (on macOS, launchd) starts at the scheduled
start and that runs the whole attempt (repository file `scripts/run_night.py`).
<!-- src: registration §0.17 l.797-798 -->

A **physical hazard** is a condition of the machine that would corrupt a measured energy if collection ran through
it. Six are registered:

1. the wall clock makes a clock step, or its rate is outside what the frequency gate allows;
2. the machine is off AC power, or its battery is charging (and, before the window starts, a battery current of more
   than 200 mA in either direction while the machine sits idle);
3. the operating system reports thermal pressure (Section 3);
4. a process that is not part of the measurement uses more than 5% of one processor core;
5. the disk has too little free space for the window's files;
6. the sampler is not delivering power records at its usual pace.
<!-- src: registration §0.15 l.750-753; §4.2 l.1269 -->
<!-- calc: items 1, 2, 3, 4, 5, 6 are list numbers -->

A **hazard check** is a program that measures the physical quantity behind one physical hazard directly, keeps the
raw bytes it read together with their SHA-256 digest, and answers PASS, REFUSE or UNMEASURED; UNMEASURED means the
measurement itself failed or ran out of time (repository label: hazard module). A test that reads a stand-in for the
quantity, such as the text of a setting or a receipt left by an earlier step, is not a hazard check.
<!-- src: registration §0.15 l.754-757 -->

The **agent census** is a listing of the machine's running processes, searched for agent sessions. It is clean when
it finds none. The project's standing rule is that no measurement starts or continues while an agent session is alive
on the machine. Outside a window, agent sessions on this machine do the project's bookkeeping, and a supervising job
stops them before each scheduled start.
<!-- src: registration preamble l.33-34; §3 l.1152-1156; §4.5 l.1370-1371, 1416-1417 -->

The **arm** is the sequence of checks the driver runs after the scheduled start to decide whether the window's chain
starts. It ends in GO only if no hazard check answered REFUSE, the sampler's own hazard check answered PASS, the agent
census is clean, and the machine's operating-system build and model are ones the calibration acceptance covers, that
is, ones its pulse calibrations were recorded on. Otherwise the window is refused and nothing is launched. An
UNMEASURED answer refuses only for the sampler, because a sampler that cannot be read is itself the hazard; for the
other five physical hazards it is recorded and the arm goes on, since each of them is measured again throughout the
window. The agent census is taken at the start of the arm, again just before GO, and then every 30 s while the chain
runs; an agent session found while the chain runs stops the chain. To arm a window is to run this sequence, and to
re-arm a pack is to schedule a new attempt of it. (In repository code the word `arm` also names a side of a quad. The
paper never uses it that way.)
<!-- src: registration §0.15 l.758-765; §0.8 l.420; §4.5 l.1418-1419; §4.7 l.1515-1516 -->
<!-- calc: five = six hazards less the sampler's -->

The arm is not the only place where the driver can decline to launch the chain. An arm that itself fails to run, or
runs out of time as a whole, ends without GO, because the sampler is then unverified. And the driver refuses in three
further cases, in each of which nothing is launched. The first is tested before the arm: the job that supervises
windows has already given this launch up, because the driver had written no record of having started, and has
released the machine. The other two are tested after GO, just before the chain is launched. Before launching, the
driver writes into the window's directories a small file that ties every member's bundle to this window's plan, and
then reads it back. It refuses if the machine has rebooted since that file was written, because instants stamped on
the monotonic clocks of two different boots cannot be placed on one time axis. It also refuses if the file cannot be
written because the pack's pinned list of member configurations is unusable: no member's configuration could then be
checked against that list, and every member would refuse itself. Any other fault in that file is recorded, and the
chain is launched.
<!-- src: registration §0.15 l.765-766; §0.17 l.805-822; §5.4 l.1790-1792; joulewise/b5/driver.py l.88-93, 2099-2107, 2273-2283 -->
<!-- calc: three further cases are the three codes of the cited code lines -->

The **dwell** is the waiting part of the arm, between 180 and 2,700 s long, in which competing processes and the
steadiness of the wall clock are measured. Process activity is measured in intervals of 30 s. The dwell ends, and the
arm goes on, once six intervals in a row, 180 s, have passed in which no outside process used more than 5% of one
core. If that has not happened within 2,700 s, the arm refuses. The arm's other steps take about 41 s, so the chain
starts between about 4 and 46 minutes after the scheduled start.
<!-- src: registration §4.1 l.1181, 1185-1186; §4.2 l.1290-1293 -->
<!-- calc: 180 / 30 = 6 intervals; 41 + 180 = 221 s, about 4 minutes; 41 + 2,700 = 2,741 s, about 46 minutes -->

The **monitor** is a background program that runs from GO until the chain's processes are gone and writes a
timestamped log of each physical hazard's quantity: the clock anchor every 1 s and the frequency word every 5 s, the
battery's state and the thermal-pressure level every 5 s, the battery's current every 1 s, each process's CPU use
every 10 s, and free disk space every 60 s. After the window these logs are joined to each member's time span, so that
a physical hazard that arises during the window removes the members it touched instead of stopping the window.
<!-- src: registration §0.17 l.824-829; §0.15 l.762-763 -->

**Battery assist** is the battery supplying part of the machine's power while the adapter is connected and the
battery is not charging. It happens under heavy load, when the machine draws more than the adapter delivers.
The battery's current is read once a second from the machine's power-management controller (Apple's System
Management Controller) and is negative when the battery discharges into the machine. Battery assist during a member
is reported and removes nothing, for two registered reasons: the processor rails are regulated downstream of the
power source, so their energy is the same whichever source delivered it; and battery assist occurs when load is
highest, so removing assisted members would select members by load. Every reported cell and both contrasts are
printed twice, with and without the members that saw battery assist. Charging and the loss of AC power during a
member still remove that member.
<!-- src: registration preamble l.81-85; §4.2 l.1244-1247, 1260-1262, 1274-1275; §9.2 l.2993-2995, 3002-3014; analysis plan §8.1 l.491-502 -->
<!-- calc: two registered reasons are items 1 and 2 of the cited ruling; both contrasts are the two contrasts -->

The **whole-machine meter** is a second, independent instrument: a power meter placed in the USB-C cable between the
adapter and the laptop, which records the voltage and current entering the machine 50 times a second (a POWER-Z
KM003C). Its measurement boundary is wider than the sampler's: the whole machine's DC input, to which the battery's
contribution is added when there is battery assist. It is a recorded cross-check. For each member, the energy that
entered the whole machine during the measured request, less what the same length of time would have drawn at the
power of the member's idle baseline, is set beside the member's idle-subtracted energy, and the second is reported as
a share of the first. The whole-machine meter never refuses a window, never removes a member, and never enters a
reported number.
<!-- src: registration §5.8 l.2023-2024, 2027-2028, 2032, 2045-2056, 2091-2092 -->

The **clock-step control** is a deliberate clock step, made by switching network time on after the chain of the first
window has ended, to show that the wall clock's hazard check can see a clock step at all: without it, a hazard check
that always answered PASS would look the same as a quiet clock (repository label: G10). Network time is switched off
again when the control ends. Its outcome is reported and touches no energy.
<!-- src: registration preamble l.41-42; §3 l.1119-1126, 1133, 1138-1139 -->

## 12. After a window: flags, the harvest, and what can support a claim

Since a window is refused only for the reasons of Section 11, everything else that goes wrong must be written down
while collection continues, and judged afterwards by rules fixed in advance.

A **flag** is one recorded fact about a window, written as one line of a file: a code naming what was observed; its
scope, which is the whole window, one stage, one quad or one member; the time interval it covers; the value observed
and the value expected; the path and SHA-256 digest of the raw bytes that show it; and an identifier, which is a
digest of the flag's own content, so that the same fact written twice is counted once. Flags are written by the arm,
the monitor, the driver and the program that processes the window afterwards. A flag never stops collection.
<!-- src: registration §0.16 l.771-774; §6.1 l.2108-2113; joulewise/flags/schema.py l.5-9, 37-39 -->

The **flag catalog** is the file, sealed together with the registration, that assigns to every flag code exactly one
of three consequences (repository file `flag_catalog.json`). **Remove the member** takes the flagged member out of
every reported cell and contrast it feeds (repository label: EXCLUDE_MEMBER). **Remove the window** means the window
can support no claim (repository label: EXCLUDE_WINDOW). **Disclose** means the flag is recorded and reported with
the results and removes nothing (repository label: DISCLOSE). The consequence of a code is fixed before any data
exist; nothing decides it after the fact. A code the flag catalog does not list stops nothing during collection, and
it must be classified, by an erratum that reads no energy, before any energy of the measurement block is read.
<!-- src: registration §0.16 l.775-780; §7.2 l.2825-2827 -->
<!-- calc: three consequences are the three named in the cited lines -->

Removal works on whole units. A removed absolute repeat removes that one unit. A removed member of a quad removes the
whole quad, so that the A, B, B, A cancellation of drift is never broken. A window is **claim-usable** when no flag
with the consequence "remove the window" fired, every paper cell of a single-model window still has at least 8 of its
10 units in each stratum, and each contrast of the contrast window still has at least 8 of its 10 quads. One further
condition applies to the contrast window alone: an attempt whose midpoint reference is a lost reference is not
claim-usable, because the whole-window drift allowance of its two contrasts would then rest on no reading taken
between the start and the end of the window.
<!-- src: registration §0.16 l.788-793; §6.6 l.2473-2478 -->
<!-- calc: two contrasts -->

Worked example, with invented removals. In a 1.7B window, idle admission aborts decode repeat 6, and one member of
decode quad 5 and one member of decode quad 9 are removed for a competing process. The decode cell keeps 9 of 10
absolute repeats and 8 of 10 quads. Both counts are at least 8, so, if the prefill cell also keeps at least 8 and 8
and no flag removes the window, the window is claim-usable. If a member of a third decode quad were removed, the
decode cell would keep 7 quads, which is below 8, and the window would not be claim-usable. The limit is 8 because a
reported cell's half-width (Section 6) is then at most about 17% larger than with all 10 units, for the same scatter.
The half-width is t × √V. V is proportional to one over the number of units, so √V grows by a factor of √(10/8),
and t rises from 2.262 at 9 degrees of freedom to 2.365 at 7: √(10/8) × 2.365 ÷ 2.262 = 1.17.
<!-- src: registration §6.6 l.2476-2483; analysis plan §4 l.228-232 -->
<!-- synthetic: repeat 6, quads 5 and 9, a third quad; calc: 10 - 1 = 9; 10 - 2 = 8; 10 - 3 = 7; 8 - 1 = 7; the square root of 10/8 is 1.118; 1.118 x 2.365 / 2.262 = 1.17, that is 17% larger; 1.7 is the model name -->

The **exclusion function** turns a window's flags into the list of what is kept. Its inputs are the flags, the flag
catalog, the pack's planned list of members and units, and each member's time span. Its output names the removed
members, the units each reported cell and contrast keeps, and whether the window is claim-usable. It reads only each
flag's code, scope, interval and identifier, and which pack the window ran. It never reads an energy, a power or a
duration, so what is removed cannot depend on a result (repository function `compute` in
`joulewise/flags/exclusions.py`).
<!-- src: registration §0.16 l.781-787 -->

The **harvest** is the program run on a window's files after its chain has exited (repository file
`scripts/harvest_b5_window.py`). It archives the files, recomputes from the preserved raw bytes every check that
protects a number, joins the monitor's logs to each member's time span, writes every flag, and runs the exclusion
function. It always emits the numbers together with the flags.
<!-- src: registration preamble l.37; §0.17 l.838-840 -->

Each attempt ends with one of four **attempt verdicts**. COLLECTED: the chain started; the numbers and the flags are
emitted whatever the flags say, and the exclusion function decides whether the window is claim-usable. NULL: the
chain never started, because the arm refused or the driver failed first. NO_COLLECTION: the chain started and stopped
before any stage of members ran. HARVEST_FAULT: the harvest itself failed on files that are present; it is repaired
and run again on the identical files, and it is never an outcome of the measurement.
<!-- src: registration §7.1 l.2781-2787 -->
<!-- calc: four verdicts, as listed -->

The **analysed window** of a pack is its first claim-usable attempt, in the order the attempts were armed. A pack is
re-armed until it has one and is never armed again afterwards, and attempts are never mixed: no member, quad or
reported cell is pooled, topped up or replaced across attempts. The decision to re-arm reads only whether an attempt
is claim-usable, never an energy.
<!-- src: registration §7.2 l.2791-2796 -->

## 13. Custody, blinding, and the code that ran

**Custody** is a directory whose files are written once, never modified, and listed with their SHA-256 digests.
<!-- src: registration §0.1 l.257 -->

**Blinding** is the rule that, from the arm of the first window until the measurement block closes (every pack has a
claim-usable attempt, or the block is ended early), nothing computed from a science member's energy is shown to a
person or an agent session, printed, emailed or committed to the repository. What may be released during that time is
called **structure**: the attempt verdicts, whether a window is claim-usable, counts of flags and of kept units, file
paths and digests, the hazard checks' measurements, and timing other than the duration of a phase. What may not is
**restricted**: energies, powers, phase durations, detection floors, the means of reported cells, dominance ratios,
the numeric outputs of the calibrations, and any pass or fail that was derived from a science member's energy. Every
flag is marked as structure or restricted.
<!-- src: registration §0.16 l.773-774; §8 l.2886-2891 -->

**Restricted custody** is custody that only programs may read while blinding holds. The harvest writes every energy
there.
<!-- src: registration §0.1 l.258-260; §7.1 l.2781 -->

The **release event** is the recorded moment from which energies may be read. It comes after the measurement block
has closed and after the whole analysis has been run once, end to end, on the real files with only structure shown,
so that faults in the analysis programs are repaired before anyone has seen a number. The record of the release event
lists the digests of the sealed registration, analysis plan and flag catalog beside the final harvest records. The
analysis then runs exactly as registered, and any analysis that was not registered is labelled exploratory.
<!-- src: registration §0.1 l.258-259; §8 l.2894-2897; analysis plan §3.2 l.186-195 -->

The **claim head** is the exact version of the repository, one git commit, whose code every window of the
measurement block runs (repository label: H_claim). The **sealed inventory** is one of the files sealed with the
registration. It lists the SHA-256 digest of every tracked file in the repository's two code directories and in the
three packs, as they are at the claim head. At each arm the driver records the digests of those files as they are on
disk, for the code directories and the window's own pack: the **executed-file inventory**. The harvest compares the
two, so that a window run on changed code is detected.
<!-- src: registration preamble l.16-17; §0.18 l.850-853; §11 l.3062-3063 -->
<!-- calc: two code directories are joulewise/ and scripts/; three packs -->
