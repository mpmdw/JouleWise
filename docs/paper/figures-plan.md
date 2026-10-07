# Figures plan: Paper A (built) and Paper B (measurement block 5)

Refreshed 2026-10-07. This plan replaces the one last changed on 2026-09-03 (commit `73d0a68ac`);
section 9 lists what changed and why.

This file plans every figure of the project's two papers.

- **Paper A** is the merged methods paper, `docs/paper/draft-v2-skeleton.md` ("JouleWise: Timing
  Sensitivity of Phase-Energy Assignments on Apple Silicon"). Its ten figures are built. This plan
  lists them and changes none of them.
- **Paper B** is the capstone paper on the energy that one Apple laptop spends in the two parts of a
  local language-model request: reading the prompt, and generating the output. Its numbers will come
  from a set of measurement runs called measurement block 5 (section 2 builds the term). It has no
  draft yet; its design sections are being written under `docs/paper/paper-b/`.

Block 5 has not been collected. No number in this plan is a result, and no sentence here says or
suggests what a result will be.

What block 5 runs, and how its data will be judged, is fixed in advance in three files in
`configs/campaigns/v5_claim_25g83/`: the **registration** (`registration_block5.md`), its **analysis
plan** (`analysis_plan_block5.md`: what is computed from the collected data, and how) and its **flag
catalog** (`flag_catalog.json`: for each kind of fact the measurement can record about a run,
whether that fact removes data from the paper's numbers; section 2 builds it). A value, rule or
sentence stated in these files is called **registered** below. This plan was written against their
revision 9 at commit `9b0c680ed`. Revision 9 is a draft: the three files bind only once an
independent review has **sealed** them, that is, frozen their bytes, and a few values may still
change before that. So every registered value typed below is followed by an HTML comment naming
where it was read (`<!-- src: reg §5.5 l.1850 -->`; "reg" is the registration, "plan" is the
analysis plan, "l." is the line in the file at that commit), and one pass after the seal can recheck
each of them.

## 1. What this plan answers

Section 4 has one row per figure. Each row states what the figure shows; the file that holds its
values (its source artifact); the measurement block that file belongs to; and the figure's class,
which says when it can be built: schematic (no measurement in it), released (measurements that may
be printed today) or waiting (measurements that block 5 has yet to produce). Section 3 gives the
exact definitions.

Sections 5 to 7 then give, for each Paper B figure, what is needed to build it: the question it
answers; the source of each **mark** (a drawn point, bar, tick or band that carries one value); the
axes and their scales; the name of every visual element; the sentences its caption must carry; and
what is left out when an input is missing. Section 8 holds the rules common to all figures, section
9 the changes from the old plan, and section 10 the points still open.

## 2. Terms used in this plan

Each term is built here before the plan uses it. Where one definition needs a term that is built a
few lines later, it says in plain words what that term means at the place it is used. The names are
those of Paper B's lexicon, `docs/paper/paper-b/01-terms.md`, which builds them in full for the
paper's reader; the short definitions here make the plan readable on its own, and section 10 lists
the terms this plan needs that the lexicon does not have. Where a plain name differs from the label
a reader will meet in the repository, the label follows once in parentheses.

- **Machine, sampler, power record, processor rails.** The machine is one Apple M3 Max laptop
  running macOS build 25G83 on a 140 W mains adapter. <!-- src: reg §0.2 l.267-268 --> The
  **sampler** is the macOS program `powermetrics`, asked for one **power record** every 100 ms. Each
  record states the average power, over its own stretch of time, of the **processor rails**: the
  supply lines of the CPU, the GPU and the neural engine, taken together.
  <!-- src: reg §0.2 l.270-273 --> Every energy Paper B reports is a processor-rail energy, never
  the energy of the whole machine. <!-- src: reg §1 l.892-893 -->
- **Member.** One inference request run in its own process. The sampler first records the idle
  machine (the member's **idle baseline**), then the request runs once untimed as a warm-up, then it
  runs again as the **measured request**. The member's **sampler stream** is one continuous run of
  the sampler from the start of the idle baseline to the end of the measured request.
  <!-- src: reg §0.3 l.277-302 -->
- **Phase, phase energy, gross.** The measured request has two **phases**. In **prefill** the model
  reads the whole prompt and computes the first output token (a token is the unit of text a model
  reads and writes, roughly a word or a piece of one). In **decode** it produces the remaining
  output tokens. A phase's **edges** are the instants at which it starts and ends. A **phase
  energy** is the sum, over the power records that overlap the phase, of each record's power times
  the length of the overlap. No idle power is subtracted, so the energy is **gross**.
  <!-- src: reg §0.4 l.307-312 -->
- **The two workloads.** The decode workload is a 42-token prompt with exactly 512 output tokens.
  The prefill workload is a prompt of exactly 2,048 tokens with 512 output tokens; **prefill-p2048**
  below means the prefill phase of this workload. <!-- src: reg §0.5 l.323-334 --> The prefill of
  the 42-token prompt is shorter than one power record, too short to measure. The registration
  expects it to fail its checks on every member, and no figure plots it.
  <!-- src: reg §0.5 l.328-330; plan §8.1 l.561-562 -->
- **Measurement block, window, stage, chain, driver.** A **measurement block** is a set of
  unattended measurement runs registered together before any of them is collected. A **window** is
  one such run: the stretch of machine time from its scheduled start to the moment its chain exits.
  The **chain** is the script that runs the window's members, in **stages**: ordered groups of
  members run one after another. The **driver** is the separate program that the operating system
  starts at the scheduled start; it launches the chain, watches it, and writes the window's last
  record. <!-- src: reg §0.6 l.342-343; reg §0.7 l.410-414; reg §0.17 l.797-798, l.803-804 -->
  Blocks 1 to 3 are closed, meaning finished, with nothing more to collect in them. Block 1 measured
  how far the sampler's timing can be off on this macOS build (by pulse calibration, built below).
  Block 2 was a first try at choosing the prompt length of the prefill workload; it stopped before
  it had run every candidate length and was closed without a choice. Block 3 tried again under a new
  registration and chose 2,048 tokens. Block 4 was planned as a qualification run (a run meant to
  test the machinery before real windows); it does not run as a block of its own and was folded into
  block 5.
  <!-- src: README.md l.13; configs/campaigns/g2a_prefill_probe_25g83/registration_block3.md l.49-58; reg §0.5 l.332-334; reg l.41-42; reg §0.7 l.412-414 -->
- **Science member.** A member whose energy enters a number the paper reports. The other members of
  a window are reference members: they run one fixed reference workload, only to watch the
  instrument and the machine (built below).
- **Pack, and the three windows of block 5.** A **pack** is the complete plan of one window: its
  stages in order and the configuration of every member. The two models measured are Qwen3-1.7B and
  Qwen3-8B; below, the **1.7B model** and the **8B model**. Both are used with their parameters (the
  numbers a model is made of) stored at 4 bits apiece, a compressed form called 4-bit quantization.
  Block 5 has three packs, run in this fixed order, and each pack's window is named after what it
  holds:
  <!-- src: reg §0.7 l.388-394; reg §7.2 l.2794-2795; sizing_b5.json packs.*.science_members, .members -->
  - the **1.7B window** (label ALPHA): 100 science members of the 1.7B model, 119 members in all;
  - the **8B window** (label BETA): 100 science members of the 8B model, 119 members in all;
  - the **contrast window** (label GAMMA): 80 science members, 40 of each model interleaved, 101
    members in all.

  The 1.7B window and the 8B window are together the **single-model windows**.
- **Attempt.** One try at running one pack. If an attempt's data cannot be used for the paper's
  numbers (the test is built below, under "claim-usable"), the same pack is tried again under a new
  attempt number. <!-- src: reg §0.7 l.409; reg §7.2 l.2794-2796 -->
- **How long a window is.** The registration gives every window two very different lengths, and a
  figure that confuses them misleads. The **expected length** of a window's chain is about 5 to 9
  hours: 5.4 h (1.7B window), 5.7 h (8B window) and 4.8 h (contrast window) projected from the code
  now in place, or 8.8, 9.1 and 7.7 h if each member takes as long as it did in block 3. The
  **deadline** is 28.4, 29.05 and 25.3 h: the time after which the driver stops a run that is still
  going. It is three to five times the expected length because it charges every member its slowest
  allowed path at once: in the 1.7B window each member is charged 672 s, where block 3 measured a
  median of 236.5 s from one member's start to the next.
  <!-- src: reg §5.5 l.1848-1852 (table), l.1859-1867, l.1875, l.1898; computed here: 28.4/8.8 = 3.2 and 28.4/5.4 = 5.3 -->

  Windows run back to back. How many fit in a day follows from three amounts of time, which the
  registration adds up.

  1. *The three chains.* 5.4 + 5.7 + 4.8 = 15.9 h on the projected figures, or 8.8 + 9.1 + 7.7 =
     25.6 h on the block-3 figures.
  2. *Each window's arm.* The expected length covers the chain only. Before its chain, each window
     spends 4 to 47 minutes in the checks that decide whether the chain may start (the arm, built
     below).
  3. *The time that follows each window before the next can start,* about 0.6 to 1.6 h. It is made
     of the driver's closing steps and its end-of-window report (about 0.1 h); up to 5 minutes until
     the scheduled job that supervises the machine next looks and sees that the window has ended; a
     few minutes of record-keeping and of writing the next window's plan; 0.5 to 1.5 h for the
     program that re-derives every check from the window's stored files (the harvest, built below),
     which is most of it; and a lead of 180 s before the next scheduled start, in which the AI agent
     sessions on the machine are stopped (the arm lets no chain start while one is alive).

  The registration's totals count the arm and that following time once for each of the three
  windows. On the projected figures that is 15.9 + 3 × 0.07 + 3 × 0.6 ≈ 18 h at the least and 15.9 +
  3 × 0.78 + 3 × 1.6 ≈ 23 h at the most; on the block-3 figures, 25.6 + 0.2 + 1.8 ≈ 28 h and 25.6 +
  2.35 + 4.8 ≈ 33 h. So the three windows take about 18 to 33 h in all, if each is usable on its
  first attempt: a rate of two to four windows per 24 hours (3 × 24 ÷ 33 = 2.2; 3 × 24 ÷ 18 = 4.0).
  These are planning figures and decide nothing. A window is therefore not a night: names in the
  repository that say `night` (`scripts/run_night.py`, the `night/` record directory) are older
  names for one window.
  <!-- src: reg §5.5 l.1895, l.1903-1908; reg §4.1 l.1185-1186; reg §3 l.1152-1157; computed here: 4 min = 0.07 h and 47 min = 0.78 h; 15.9 + 0.2 + 1.8 = 17.9; 15.9 + 2.35 + 4.8 = 23.05; 25.6 + 0.2 + 1.8 = 27.6; 25.6 + 2.35 + 4.8 = 32.75 -->
- **Absolute repeat, quad, unit.** An **absolute repeat** (below, a repeat) is one science member
  run on its own; the single-model windows each run ten in a row for each workload. A **quad** is
  four consecutive science members in the order A, B, B, A, where A and B are two conditions. The
  order makes a steady drift fall equally on A and B: if each member reads δ more than the one
  before it, the two A members carry 0 and 3δ and the two B members δ and 2δ, and both pairs average
  1.5δ. In the single-model windows A and B are the same model and workload (a **null quad**), so
  any A-versus-B difference can only come from the instrument and the machine. In the contrast
  window A is the 1.7B model and B the 8B model. Each repeat and each quad is one **unit**: the
  statistics treat a unit as one independent draw. That independence is an assumption, and every
  interval carries it. <!-- src: reg §0.8 l.418-434 -->
- **Pulse calibration, pulse timing bound, bracket.** A **pulse calibration** (below, a calibration)
  is one run of the sampler (a **capture**) during which the GPU is driven through 59 commanded
  on/off power pulses. Fitting the power records to the commanded times gives the largest timing
  error between a commanded edge and the edge the records show: the capture's **pulse timing bound**
  (the registration calls it the fiducial bound). Each window is enclosed by one calibration before
  its first member, the **pre calibration**, and one after its last, the **post calibration**; the
  pair is the window's **bracket**. <!-- src: reg §0.11 l.458-463 --> The **calibration ledger** is
  the file, only ever appended to, that records every calibration capture taken on the machine.
  Before a window's pre calibration the chain makes the **bracket reservation**: it opens an entry
  in the calibration ledger that names the window's plan, and the window's pre and post calibrations
  are then recorded against that entry (repository label: bracket session). If the entry cannot be
  opened, the window's two calibrations have nothing to be recorded against, and the chain stops.
  <!-- src: reg §0.11 l.470-477; reg §5.1 l.1536, l.1543 -->
- **Reference members and the reference drift check** (repository label NEG-8, an inherited name and
  not an abbreviation). A **reference member** is a member of one fixed reference workload, run only
  to watch the instrument and the machine and never reported. Each window runs 12 of them at its
  start (the **reference corpus**), then three more just before the science members (the **start
  triplet**), one at the middle of the window, after the science members of the decode workload and
  before those of the prefill workload (the **midpoint reference**), and three after the last
  science member (the **end triplet**). <!-- src: reg §0.12 l.489-495 --> From the corpus the
  registration computes a **reference drift bound**: how far apart a start mean and an end mean
  could lie through the corpus's own scatter alone. The **reference drift check** passes when the
  mean of the end triplet and the mean of the start triplet differ by no more than that bound. The
  **whole-window drift allowance** is the larger of the bound and the spread of three values (the
  start mean, the midpoint reference's energy and the end mean); it enters the intervals of sections
  7.2 and 7.3 as one of the bounds they add. <!-- src: reg §0.12 l.511-534 --> A reference that
  failed, or was contaminated (for example, another process was busy during its request), is a
  **lost reference**: it is dropped, and the check runs on the **surviving references**, which must
  number at least two in the start triplet and two in the end triplet. Each of the three later
  reference stages may run **spares** once, to stand in for members it lost: three for the start
  triplet, three for the end triplet, one for the midpoint. Spares are extra reference members named
  in the registration in advance. The contrast window also runs two **interior references**, one in
  the middle of its decode half and one in the middle of its prefill half (after science members 20
  and 60 of its 80); they are recorded, and no check uses them.
  <!-- src: reg §0.12 l.496-510, l.535-536, l.601-604, l.615-616 -->
- **Physical hazard, arm, dwell, monitor.** A **physical hazard** (below, a hazard) is a condition
  of the machine that would corrupt a measured energy if collection ran through it. Six are
  registered: the clock jumping (a step) or drifting too fast; the battery charging, or the adapter
  not supplying the machine; thermal pressure (the operating system reporting that heat is limiting
  the processor); another process using more than 5% of one processor core; too little free disk;
  and the sampler not producing records at its expected rate. The **arm** is the sequence, run at a
  window's scheduled start, that measures each hazard directly and decides whether the window's
  chain starts (go) or does not (refuse). Part of the arm is the **dwell**, a wait of 3 to 45
  minutes during which other processes and the clock are observed. Once the arm says go, a
  background process, the **monitor**, keeps measuring the hazards until the window ends.
  <!-- src: reg §0.15 l.750-759; reg §4.1 l.1181; reg §0.17 l.824-828 -->
- **Member clock bound, frequency word, frequency gate.** Power records and phase edges are stamped
  on different clocks. Placing one against the other is good only to within a per-member **member
  clock bound**, and a member whose bound exceeds 5 ms is removed. One part of the bound comes from
  fitting the time labels the records themselves carry; in block 3 it was at most 3.6 ms. The other
  part grows with the rate at which the operating system is correcting the wall clock (a kernel
  value, the **frequency word** f, in parts per million) times the length of the member's sampler
  stream. The **frequency gate** is the arm's check that predicts the worst member's bound before
  any member runs. <!-- src: reg §0.14 l.720-746; reg §4.2 l.1199-1200 -->
- **Harvest, flag, flag catalog.** The **harvest** is the program run after a window ends; it
  re-derives every check from the window's stored raw files and writes the window's records. A
  **flag** is one recorded fact about a window, a stage, a quad or a member, for example that
  another process was busy during a member's request. A flag never stops collection. The **flag
  catalog** gives every flag code exactly one **effect**: the member is removed from the numbers it
  feeds; the whole window is removed; or the fact is only **disclosed**, that is, recorded and
  printed with the results while removing nothing.
  <!-- src: reg §0.16 l.771-780; reg §0.17 l.838-840 -->
- **Reported cell.** One registered energy number for one model and one phase, computed from that
  model's 10 repeats and 10 null quads (50 members). Paper B prints four: decode and prefill-p2048,
  for each of the two models. <!-- src: reg §0.9 l.438-443 -->
- **Kept unit, claim-usable, analysed window.** A **kept unit** is a repeat or a quad none of whose
  members a flag removed. A quad with one removed member is removed whole, so that its drift
  cancellation is not broken. A window is **claim-usable** when no window-removing flag fired and
  every number it reports still rests on at least 8 of its 10 repeats and at least 8 of its 10
  quads. (The comparison of the two models in the contrast window, built below as a contrast, uses
  quads only; and on the contrast window a lost midpoint reference also makes the attempt not
  claim-usable.) The **analysed window** of a pack is its first claim-usable attempt; no other
  attempt feeds any number.
  <!-- src: reg §0.16 l.788-793; reg §6.6 l.2473-2478; reg §7.2 l.2791-2793 -->
- **Detection floor and its steps.** The **detection floor** of a model and phase is the largest
  difference the instrument produces when nothing differs, and hence the smallest real difference it
  can resolve. It is estimated in two **forms**: the **absolute form**, from the scatter of the kept
  repeats, and the **comparative form**, from the A-versus-B differences of the kept null quads.
  <!-- src: reg §0.10 l.447-450; plan §5 l.284-293 --> Each form is built in steps, which section
  7.1 draws. The **point floor** takes every value at its measured point. The **corner-widened
  floor** lets each value lie anywhere within its **timing uncertainty** (in joules: how far the
  value could move if the power records were placed in time anywhere the timing bounds allow) and
  takes the largest floor that results. The analysis finds it by computing the floor for every
  combination in which each value sits at one end or the other of its range; each such combination
  is a corner (n values have 2ⁿ of them), hence the name. The **guard** is a factor that enlarges
  the floor when fewer than 10 units were kept. Last, the code that writes the floors to their file
  adds the whole-window drift allowance (section 10, point 6).
  <!-- src: plan §5 l.295-309; joulewise/detection_floor.py l.1480-1521, l.1636-1659 -->
- **Attribution floor.** A different quantity from the detection floor: an estimate, about 1 J, of
  how much phase energy can be assigned to the wrong phase because phase edges are timed only to
  within the sampler's timing error. It is printed beside a reported cell and never added to its
  interval. No file yet fixes its value for this macOS build.
  <!-- src: reg §0.10 l.451-454; reg §14 Q5 l.3302-3303 -->
- **Dominance ratio R.** For one model, phase and form: the corner-widened floor divided by the
  point floor, both taken before the guard. R of at least 2 means that timing uncertainty at least
  doubles the floor. <!-- src: plan §6 l.344-348 -->
- **Contrast, its two intervals, its outcome.** In the contrast window each quad gives one
  difference: the mean of its two 8B-model members minus the mean of its two 1.7B-model members. A
  **contrast** is the mean of those differences over the kept quads, for one phase. There are two:
  decode and prefill-p2048. <!-- src: reg §0.8 l.427-428; plan §7.1 l.369-377 --> A contrast's
  **metrology interval** is a 95% interval from two sources: the quad-to-quad scatter of those
  differences, and the random error that each member's own record states for its phase energy (as a
  variance). Its **decision interval** is the metrology interval widened on both sides by the bounds
  each member records for timing and for drift. <!-- src: plan §7.1 l.387-398 --> The floor a
  contrast must exceed is the larger of the two models' detection floors for that phase.
  <!-- src: plan §5 l.330-333 --> Because two contrasts are tested, their p-values are adjusted by
  Holm's method, which keeps the chance of any false positive across the two at 5%.
  <!-- src: plan §7.1 l.399-401; reg §0.19 l.864 --> The analysis gives each contrast one
  **outcome**: not estimable (an input the calculation needs is missing or invalid, for example a
  member's phase energy that is absent or not a finite number); not resolvable (for example, the
  estimate does not exceed the floor); unresolved (the metrology interval contains zero, or the
  adjusted test does not reject); or direction supported (none of the above). "Direction supported"
  asserts the sign of the difference, that is, which model used more phase energy. It is not a
  statement about the size of the difference, which is read from the estimate and its intervals.
  <!-- src: plan §7.2 l.408-421 -->
- **Battery assist.** Under heavy load the battery can supply part of the machine's power while the
  adapter is connected and the battery is not charging. A member that was not removed and whose
  measured request saw this is an **assist member**. Assist is disclosed, not removed, and every
  reported cell and both contrasts are computed twice: with, and without, the units that hold an
  assist member. <!-- src: reg §9.2 l.3012-3014; plan §8.1 l.483-503 -->
- **Whole-machine meter, and the three quantities read from it.** An inline USB-C power meter
  between the adapter and the laptop records the power entering the whole machine 50 times a second.
  It never enters a reported number; it supports one descriptive cross-check. For each member's
  measured request the harvest computes **ΔE_rail**, the processor-rail energy above the member's
  idle baseline; **ΔE_machine**, the energy entering the machine above the same baseline (the
  meter's reading plus what the battery discharged); and **ρ** = ΔE_rail ÷ ΔE_machine, the rails'
  share of the machine's extra energy. <!-- src: reg §5.8 l.2023-2024, l.2049-2056, l.2091-2092 -->
- **Release event.** While block 5 is being collected the analysis is blind: energies, powers and
  everything computed from them are **restricted**, and only structure (whether a window was
  collected and is claim-usable, flag counts, kept-unit counts, file hashes) may be read. The
  **release event** is the recorded moment, after the block has closed and a full dry run of the
  analysis has completed on the real bytes without showing its numbers, from which the energies may
  be read. <!-- src: reg §8 l.2886-2897 -->
- **Artifact, schema, field, refusal, slot.** An **artifact** is a file written by one step of the
  registered analysis; the plan says the step **issues** it. Its **schema** is the named, versioned
  list of its fields, for example `joulewise.claim_verdicts.v1`. Every mark in a data figure is one
  **field** of one artifact. A step **refuses** a value when one of its registered conditions fails:
  it writes a reason code and no number. A **slot** is a named place in Paper B's text or figures
  that one such field will fill; the slots are listed in `docs/paper/paper-b/slots.json`, which is
  being written alongside this plan. This plan names schema and field, and coins no slot id.

## 3. The three classes, and the states

Every figure has exactly one **class**. The class says what kind of thing the figure plots, and
therefore when it can be built.

- **schematic**: the figure plots no measurement. It is drawn from the registered design, computed
  from registered constants, or uses synthetic numbers that are labelled SYNTHETIC on the figure
  itself. It can be built at any time.
- **released**: the figure plots measurements whose values may be read and printed today, because
  they come from a closed block or from the historical diagnostic captures of Paper A, never from a
  block-5 window. "Released" describes the plotted values; the raw captures behind Paper A's
  historical figures are retained by the project and are not public (`draft-v2-skeleton.md` l.39).
- **waiting**: the figure plots block-5 measurements. No mark of it can be drawn before block 5 is
  collected and the release event is recorded.

Every figure also has one **state**: *built* (the file is committed); *in build* (being built on
branch `paper/2026-10-07-paper-b` alongside this plan, and not yet committed when this plan was
written); *held* (class released, but no ruling yet says which of its values may be printed);
*waiting* (class waiting); *not planned*.

## 4. Every figure, one row each

"Block" names the measurement block whose data or design the figure rests on. "None" means the
figure rests on no block.

### 4.1 Paper A (all built; files under `docs/paper/figures/`)

The ids in parentheses in the source column (SYN-08 and the like) are row ids of
`docs/paper/results-fill-registry.md`, the table that ties each printed value of Paper A to its
source.

| Printed label | File | Shows | Source artifact | Block | Class | State |
|---|---|---|---|---|---|---|
| Figure 1 | `fig1_boundary_attribution.svg` | One power record split at two candidate phase boundaries, and the energy that changes phase | Constants in `build_mechanism_figures.py` (SYN-08) | None: synthetic numbers | schematic | built |
| Figure 2 | `fig4_edge_excursions.svg` | Pulse timing lags fitted from one retained historical capture | `docs/paper/round7/excursion-decomposition.json`, written by `scripts/paper_excursion_decomposition.py` (DX-001, DX-003, DX-010 to DX-013) | None: a historical diagnostic capture, taken before block 1 | released | built |
| Figure 3 | `fig5_phase_record_overlap.svg` | A phase overlapping two power records, and three | Static SVG, relabelled by `build_mechanism_figures.py`; no data | None | schematic | built |
| Figure A1 | `figA_partial_record_enclosure.svg` | Synthetic power records and one fixed time interval: the point value, the timing envelope and the enclosure of the energy assigned to the interval | `figA_partial_record_enclosure.json`, written by `scripts/paper/partial_record_enclosure.py` (PE-01) | None: synthetic numbers | schematic | built |
| Figure A2 | `fig2_window_timeline.svg` | One measurement window as designed before block 5, and the A, B, B, A order | Static SVG, relabelled by `build_mechanism_figures.py`; no data | None | schematic | built |
| Figure A3 | `figA3_block_corners.svg` | Synthetic interval endpoints enumerated: four corners, the bound at each, and the largest | Constants in `build_mechanism_figures.py` (SYN-05) | None: synthetic numbers | schematic | built |
| Figure A4 | `figA4_shared_signs.svg` | A synthetic calculation over shared and local signs, eight cases | `worked-examples.json`, member `synthetic` (SYN-01) | None: synthetic numbers | schematic | built |
| Figure A5 | `figA5_clock_polygon.svg` | A synthetic intersection of clock constraints | Constants in `build_mechanism_figures.py` (SYN-07) | None: synthetic numbers | schematic | built |
| Figure A6 | `figA6_pulse_fit.svg` | One historical calibration pulse: records, fitted averages, commanded times, enclosing rectangle | `worked-examples.json`, member `historical` (DG-134) | None: a historical diagnostic capture, taken before block 1 | released | built |
| Figure P1 | `fig3_decision_gates.svg` | Refusal of invalid evidence, then the two checks a comparison must pass | Static SVG, relabelled by `build_mechanism_figures.py`; no data. Used only by `docs/paper/protocol/prospective-comparison-protocol.md` | None | schematic | built |

`docs/paper/figures/README.md` describes each of these ten and how to regenerate them. Figure A2
shows the window as it was before block 5; for Paper B it is superseded by B-S1 below, and Paper A
keeps it unchanged.

### 4.2 Paper B, buildable now (files under `docs/paper/figures/b5/`)

The ids B-S1 to B-D6 are working ids for this plan. Printed figure numbers are assigned when Paper
B's sections are assembled.

| Id | File | Shows | Source artifact | Block | Class | State |
|---|---|---|---|---|---|---|
| B-S1 | `figB_S1_window_timeline.svg` | One block-5 window in time order, from its scheduled start to its last record | reg §5.1, §5.4, §3 and §0.12; the stage lists of `sizing_b5.json` (`packs.*.stages`) | Block 5: its design, no data | schematic | in build |
| B-S2 | `figB_S2_measurement_boundary.svg` | The path of power from the wall socket to the processor rails, and where each instrument reads it | reg §5.8 (the path drawing at l.2011-2019 and the element list at l.2021-2033) | Block 5: its design, no data | schematic | in build |
| B-S3 | `figB_S3_decision_flow.svg` | What can stop a window before it starts, what becomes a flag instead, and how flags decide whether a window is claim-usable | reg §4.1, §0.15, §0.16, §0.17, §5.1, §6.6, §7.1 and §7.2; `flag_catalog.json` | Block 5: its design, no data | schematic | in build |
| B-S4 | `figB_S4_reference_survivors.svg` | The reference members of one window, a lost reference and its spare, and the reference drift check on the surviving references | reg §0.12, with the synthetic worked example at l.670-690 | Block 5: its design, with synthetic numbers | schematic | in build |
| B-S5 | `figB_S5_frequency_gate.svg` | The largest member clock bound predicted for any member, against the rate at which the wall clock is being corrected, with the registered limit | reg §4.2 l.1199-1204 and the `clock` thresholds of reg §4.3 l.1338-1339 | Block 5: registered constants, no data | schematic | in build |

Build scripts: `build_window_and_flow.py` (B-S1, B-S3) and `build_boundary_survivors_gate.py` (B-S2,
B-S4, B-S5), with captions in `captions-s1-s3.md` and `captions-s2-s4-s5.md`, all in the same
directory.

### 4.3 Paper B, from a closed block (held)

| Id | File | Shows | Source artifact | Block | Class | State |
|---|---|---|---|---|---|---|
| B-R1 | none yet | The pulse timing bound of each calibration capture: the 17 captures of the previous macOS build beside the 24 captures of build 25G83 | `configs/calibration/calibration_acceptance_d079_v2_n17_r3.json` and `configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json`, with the calibration captures each was derived from | Block 1 for build 25G83; the previous build's captures predate block 1 | released | held |

<!-- src: reg §0.11 l.464-466 (24 captures, the 25G83 file); draft-v2-skeleton.md l.157 and l.1250 (17 captures, the n17_r3 file) -->

### 4.4 Paper B, waiting for block 5

| Id | Was | Shows | Source artifact (schema or file, then fields) | Block and windows | Class | State |
|---|---|---|---|---|---|---|
| B-D1 | Figure A | For each model and phase, the steps that build each form of the detection floor, and which form sets that model's floor for the phase | `joulewise.detection_floor_artifact.v2`: per model and phase `floor_abs_j`, `floor_cmp_j`, `floor_gate_j`, and the step fields of section 7.1 inside `absolute` and `comparative`. `joulewise.d165_dominance_closeout.v1`: `independent_ratios` (`point_unguarded_floor_j`, `corner_widened_unguarded_floor_j`, `ratio`) | Block 5: single-model windows | waiting | waiting |
| B-D2 | Figure B | The four reported cells: mean gross phase energy per request with its interval | `joulewise.paper_reported_energy_projection.v1`: `mean_j`, `lower_j`, `upper_j`, `per_token.j_per_token`, `n_bundles`, `interval.n_r`, `interval.n_b`, `interval.h_j`, `binding.attribution_floor_j` | Block 5: single-model windows | waiting | waiting |
| B-D3 | Figure C | The two contrasts: estimate, both intervals, the floor, the outcome | `joulewise.claim_verdicts.v1`, one record per contrast: `estimator.estimate`, `estimator.n`, `estimator.metrology_aware_CI95`, `deterministic_bounds.decision_interval`, `floor.active_floor_j`, `multiplicity.adjusted_p`, `claim_evaluation.outcome` | Block 5: the contrast window, with floors from the other two | waiting | waiting |
| B-D4 | Figure E, drift part | For each analysed window, the reference energies at start, midpoint and end against the reference drift bound, and the battery temperature across each stage | Harvest records of each analysed window: `derived/neg8-screen.json`, `derived/neg8-allowance.json`, the record of the reference drift check that the latter names (`start`, `midpoint`, `end`, `derived_repeatability_bound_j`, `drift_allowance_j`), and `battery_temperature_readings` in each stage's manifest (the record of a stage that the program running its members writes) | Block 5: each of the three analysed windows | waiting | waiting |
| B-D5 | new | For each member, processor-rail energy against whole-machine energy, and the rails' share | `withheld/meter.json` of each analysed window: per member `rail_delta_J`, `machine.delta_J`, `machine.battery_term_available`, `rho`; the `meter.*` flags in `derived/flags.jsonl` | Block 5: each of the three analysed windows | waiting | waiting |
| B-D6 | new | Each reported cell and each contrast, with and without the units that hold an assist member | The with-and-without-assist values registered in plan §8.1 (l.483-507), to be written by a program of the analysis that does not exist yet (section 7.0) | Block 5: all three analysed windows | waiting | waiting |

### 4.5 Dropped from the old plan

- **Old Figure D** and two parts of **old Figure E** drew on a separate campaign of measured checks
  of the instrument itself, which the old plan called the characterization campaign. Old Figure D
  (its title was "known-signal characterization") tested how the instrument responds to workloads of
  known size: whether measured energy rises in step with the number of output tokens, whether two
  identical workloads read the same, and whether a small deliberate difference is seen. Old Figure
  E's phase-consistency panels checked whether the assignment of energy to phases is consistent with
  itself. Old Figure E's settling panel plotted one further quantity of that campaign, a recovery
  time in seconds, which the old plan named and did not define. That campaign was removed from the
  paper's scope by a decision of 2026-09-08 (decision D-177) and was not run, so these panels have
  no source and are not planned. Block 5's analysis plan registers no recovery-time quantity either;
  the waits between one member and the next are recorded, and this plan draws no figure of them. The
  limitation that follows from the decision is a caption sentence of every figure that plots a phase
  energy (section 8, rule 9).
  <!-- src: docs/decision_log.md entry D-177; the old plan (this file at commit 73d0a68ac) l.131-205; reg §8 l.2888-2889 (cooldown waits are recorded and releasable) -->

Tables of flag counts, exclusions, kept units and members collected are tables, not figures, and are
outside this plan.

## 5. Paper B schematic figures: what each must show

Each of these is being built now. This section is the contract between the plan and each figure's
builder (the script that draws the figure, and its author): the question, the source, and the list
of elements that the figure or its caption must name. A reader who sees a shape that nothing names
will read it as "a box", and will be right.

### 5.1 B-S1, the window timeline

*Question.* In what order does one window do its work, and where in that order do the checks that
protect the numbers sit?

*Source.* reg §5.1 l.1536-1549 (the chain's order and its only stops), §0.6 l.342-353 (the waits
before each stage and between members), §0.12 l.489-510 (references and spares), §5.4 l.1762-1767
(the tail), §3 l.1119-1124 (the deliberate clock step at the tail), §4.1 l.1174-1186 (the arm);
stage ids and member counts from `sizing_b5.json`.

*Elements to name, in time order.*

1. The scheduled start, and the arm that follows it: its reads and its dwell, together 4 to 47
   minutes. <!-- src: reg §4.1 l.1181, l.1185-1186 -->
2. The bracket reservation (section 2: the chain opens this window's entry in the calibration
   ledger), and the pre calibration with its **pre screen**: a limit on that capture's pulse timing
   bound. The chain stops itself in three cases only, all before the first member: the bracket
   reservation fails (no entry could be opened), the pre calibration's capture fails, or its pulse
   timing bound is above the pre screen. (The driver can also stop the chain from outside; B-S3
   names those cases.) <!-- src: reg §5.1 l.1536, l.1543-1549; reg §0.11 l.475-477 -->
3. The **settles**: a 60 s wait before the pre calibration and before each of the ten stages that
   run members, eleven in all, so that the machine is idle when a stage begins.
   <!-- src: reg §0.6 l.342-344 -->
4. The reference corpus (12 members) and the computation of the reference drift bound from it.
5. The three later reference stages, each followed by the decision whether to run its spares: the
   start triplet (3 members) before the first science stage; the midpoint reference (1 member)
   between the decode stages and the prefill stages of element 6; and the end triplet (3 members)
   after the last science stage. <!-- src: reg §0.12 l.492-495; reg §5.1 l.1536-1541 -->
6. The science stages. In the single-model windows, for the decode workload and then for the prefill
   workload: one stage of 10 repeats and two stages of 20 members (five quads each). In the contrast
   window: four stages of 20 members (five quads each), two for decode and two for prefill-p2048,
   with one interior reference in the middle of each pair (after science members 20 and 60). The
   midpoint reference of element 5 therefore runs after science member 50 of 100 in the single-model
   windows and after science member 40 of 80 in the contrast window.
   <!-- src: sizing_b5.json packs.*.stages; reg §0.12 l.492-494, l.503-508 -->
7. The **cooldown** between two members of a stage: the chain reads idle processor power in 5 s
   readings and starts the next member at the first reading that is at most twice the previous
   member's idle baseline while the operating system reports its thermal state as nominal (no
   thermal pressure), or after 300 s, whichever comes first. The first member of a stage has no
   cooldown. <!-- src: reg §0.6 l.350-354 -->
8. The post calibration, which closes the bracket.
9. The tail: the chain exits; the driver proves its processes gone and counts what was collected;
   once in the block (in practice at the tail of the first 1.7B window) the **clock-step control**
   then runs, a deliberate clock step applied to show that the clock check can see one; the two
   background recorders stop; the last record is written.
   <!-- src: reg §5.4 l.1762-1767; reg §3 l.1119-1124 -->
10. The two background recorders that run from the arm's decision to the tail, drawn as bands along
    the whole window: the monitor, and the program that reads the whole-machine meter.
    <!-- src: reg §0.17 l.824-837 -->
11. The harvest, after the window has ended.

*Rule for the time axis.* The axis is elapsed time from the scheduled start, in hours. It is as long
as the arm (at most 47 minutes) plus the expected length of the chain (section 2: about 5 to 9 h).
The deadline (25.3 to 29.05 h) is written as a labelled note at the right edge, never drawn to
scale. Drawn to scale, the deadline would make the working part of the window look like a fifth to a
third of it, and a reader would conclude that the machine does one window a day.
<!-- src: reg §5.5 l.1848-1852 -->

*Second panel, recommended.* The block as three windows back to back in the fixed order. Each window
is drawn as its arm (4 to 47 minutes) and its chain, followed by the 0.6 to 1.6 h that must pass
before the next window can start, with the harvest named inside that interval; the panel carries the
sums of section 2 (about 18 to 33 h for the three windows, two to four windows per 24 hours). This
panel was not asked of the builder; if B-S1 is committed without it, it is a follow-up (section 10,
point 8). <!-- src: reg §5.5 l.1895, l.1903-1908 -->

### 5.2 B-S2, the measurement boundary

*Question.* Which energy do the reported numbers cover, which energy does the whole-machine meter
cover, and what does neither see?

*Source.* reg §5.8 l.2009-2033.

*Elements to name, from the wall inward.* Mains AC. The 140 W adapter, with the note that its
AC-to-DC conversion loss happens before the meter and is not measured. The USB-C cable at 28 V. The
inline meter, which reads the cable's voltage and current 50 times a second. The laptop's DC input.
Inside the laptop: the processor rails, which the sampler reads; and the rest of the machine
(memory, storage, fans, the sleeping display). The battery, with its current and voltage read once a
second from the laptop's power controller, and an arrow showing that when it assists it feeds the
machine beside the DC input, where the meter cannot see it. <!-- src: reg §5.8 l.2011-2030 -->

*Two outlines, each named.* The **claim boundary** encloses the processor rails only. The
**cross-check boundary** encloses the DC input and the battery's contribution; it excludes the
adapter's loss. <!-- src: reg §5.8 l.2029-2033 -->

### 5.3 B-S3, the decision flow

*Question.* When a check fails, does the window stop, or is a fact recorded? And how do recorded
facts decide whether the window's numbers may be claimed?

*Source.* reg §4.1 l.1174-1193, §0.15 l.750-767, §0.17 l.805-820, §5.1 l.1543-1551, §0.16 l.771-793,
§6.6 l.2473-2478, §7.1 l.2781-2787, §7.2 l.2791-2796.

*Elements to name.*

1. The arm, with the six hazards of section 2, each named by the quantity that is measured.
2. The two further conditions that refuse at the arm: an AI agent session alive on the machine, and
   a macOS build that no calibration has judged. <!-- src: reg §0.15 l.758-760 -->
3. The outcome "refuse": the attempt ends with nothing launched, and the same pack is armed again
   once the hazard is gone. <!-- src: reg §4.1 l.1187; reg §7.1 l.2783 -->
4. A hazard probe that failed to measure, as distinct from one that measured a hazard: for the
   sampler it refuses; for the other five it is a disclosed flag and the arm goes on. An arm that
   itself failed or timed out as a whole also ends the attempt with nothing launched, because the
   sampler was then never verified. <!-- src: reg §0.15 l.761-766 -->
5. The outcome "go", and the two cases in which the driver still refuses the window after "go" and
   before it launches the chain. At that point the driver writes, into each directory that will
   receive the window's results, a small file that ties every member to this window's plan (the
   registration calls it the launch lineage), and reads it back. It refuses the window if the
   machine has rebooted since the file was written: the members' time stamps would then come from
   the clocks of two different boots and could not be placed on one time axis. It also refuses if
   the file cannot be written, even on one retry, because the pack's committed inventory (the record
   of its members' configuration files) cannot be used: no member could then check its own
   configuration against it, and every member would refuse itself. Any other fault of that file is a
   disclosed flag, and the chain launches. <!-- src: reg §0.17 l.805-820 -->
6. The three stops of the chain before the first member (B-S1, element 2).
7. The four cases in which the driver stops a running chain from outside: free disk below its limit;
   an AI agent session appearing; the monitor silent for about 10 minutes; the deadline.
   <!-- src: reg §5.1 l.1546-1549 -->
8. Every other check: one flag, written, and collection continues.
9. The flag catalog's three effects: the member is removed; the window is removed; disclosed only.
10. Kept units, and the test for claim-usable: at least 8 of 10 repeats and at least 8 of 10 quads
    for every number the window reports, and no window-removing flag.
11. The two ends: a claim-usable attempt becomes the pack's analysed window; any other attempt feeds
    no number, and the pack is armed again.

### 5.4 B-S4, reference members and surviving references

*Question.* What does the reference drift check compare, and what happens to it when a reference
member is lost?

*Source.* reg §0.12 l.489-534 and l.601-626; the synthetic example at l.670-690. Every number in the
figure is from that example and the figure is labelled SYNTHETIC.

*Elements to name.* The 12 corpus energies, and the reference drift bound computed from them. The
three members of the start triplet, one of them lost because the machine was not idle before its
request, so the request was never measured. The spare that ran in its slot, marked as a spare. The
midpoint reference. The three members of the end triplet, one of them lost at the harvest because
another process was busy during its request; no spare runs for a loss found at the harvest. The mean
of the surviving start-triplet members and the mean of the surviving end-triplet members. The
reference drift bound for three surviving start and two surviving end members, drawn as a band. The
difference of the two means, drawn against the band. The whole-window drift allowance.

*Numbers the figure must reproduce from the example.* Start mean 99.9600 J; end mean 100.2250 J;
difference 0.2650 J; bound for the planned three and three, 0.5933 J; bound for three and two,
0.6383 J; allowance 0.6383 J. <!-- src: reg §0.12 l.672-681 -->

### 5.5 B-S5, the clock frequency gate

*Forcing problem.* Section 2 builds the member clock bound, the frequency word f and the frequency
gate. A member whose bound exceeds 5 ms is removed, and the bound grows with |f| times the length of
the member's sampler stream. A window that started while |f| was too large would therefore lose the
members with the longest sampler streams. The gate predicts the worst case before any member runs,
so that such a window does not start. <!-- src: reg §0.14 l.725-746 -->

*The registered formula.* Predicted bound = 3.7 ms + (|f| + 0.25 ppm) × 335 s, which must not exceed
5 ms. Here 3.7 ms is the largest value the first part of the bound took in block 3 (3.6 ms) plus a
0.1 ms margin; 0.25 ppm allows for the rate during a sampler stream differing from the stored value;
and 335 s is the longest sampler stream any block-5 member can have. The gate passes for |f| up to
3.6306 ppm. <!-- src: reg §4.2 l.1199-1202; reg §5.5 l.1797-1800 -->

*Elements to name.* Horizontal axis: |f| in ppm. Vertical axis: predicted bound in ms. The straight
line of the formula. The horizontal limit at 5 ms. The value of |f| at which the line meets the
limit. The two worked points of the registration: at f = −3.17 ppm the bound is 4.846 ms and the
gate passes; at |f| = 3.7 ppm it is 5.023 ms and the gate refuses. The pass region and the refuse
region, each labelled. <!-- src: reg §4.2 l.1202-1204 -->

*Class note.* Every drawn value is a registered constant or computed from one. The figure plots no
measurement of a block-5 window and is labelled as computed from registered constants.

## 6. Paper B figure from a closed block: B-R1 (held)

*Question.* How large is the timing error between commanded and observed power edges on this
machine, and how does the calibration issued for macOS build 25G83 compare with the one it replaced?

*Source and block.* Section 4.3. The 24 captures of build 25G83 are block 1's. The 17 captures of
the previous build are the corpus Paper A describes in its section 2 and Appendix A.3.8.

*Planned marks.* Two columns, one per macOS build. In each, one dot per capture at that capture's
pulse timing bound, in milliseconds on a shared vertical axis. For build 25G83, the two screens
defined by its **calibration acceptance** (the file of limits against which a window's calibrations
are judged): the largest bound among its captures, as a labelled horizontal line (a window whose pre
calibration exceeds it stops before any member; this is the pre screen of B-S1), and the range of
the bounds (their largest minus their smallest), as a labelled vertical span. The registration calls
this range the bracket screen, and it is used when a window's bracket is judged: the allowance made
for timing drift between the window's pre and post calibrations is the larger of two values, the
absolute difference between their two pulse timing bounds and this range, and that allowance must
not exceed a ceiling the calibration acceptance also fixes. <!-- src: reg §0.11 l.464-469 -->

*Why it is held.* Whether per-capture values of blocks 1 to 3 may be printed has not been ruled. No
value of either file was read for this plan, and nothing is drawn until that ruling exists. It is
also not verified which file holds the per-capture bounds: the calibration acceptances, or the
calibration ledger (section 2) they were derived from. <!-- src: reg §0.11 l.470 -->

## 7. Paper B data figures (waiting)

### 7.0 What every data figure waits for

1. **Collection.** Each pack named in its row has an analysed window.
2. **The release event.** Before it, the plotting code runs only on synthetic fixtures, that is,
   input files with made-up numbers (section 8, rule 11).
3. **Analysis programs that do not exist yet.** The program that issues the reported cells; the
   **disclosure program**, which is to write the values printed beside the results (the
   with-and-without-assist values of B-D6, the reference-drift values of B-D4 and the cross-check of
   B-D5); and the changes that let floors and contrasts read the whole-window drift allowance the
   harvest recorded. Until the last of these lands, every block-5 floor is refused by the analysis
   code, and so is a contrast whose reference drift check the harvest re-ran on surviving
   references. <!-- src: plan §11 l.659, l.662, l.669; reg §14 Q13 l.3341-3346 -->
4. **A placement ruling.** Under the paper-scope decision in force (D-174), no block-5 value has a
   place in a paper; each needs a ruling first.
   <!-- src: plan §9 l.615-617; reg §14 Q4 l.3300-3301 -->

The plotting code for these six figures is planned as `docs/paper/tools/paper_b_figures.py`, tested
on synthetic fixtures under `docs/paper/figures/b5/synthetic/`. It should take this section as its
specification.

### 7.1 B-D1, how each detection floor is built

*Question.* For each model and phase, which of the two forms sets that model's floor, and how much
of each form's floor comes from timing uncertainty and how much from run-to-run scatter?

*Source.* Two files of the registered analysis, whose steps the analysis plan numbers in its section
3.1. <!-- src: plan §3.1 l.159-172 -->

- The floor file of step 5, schema `joulewise.detection_floor_artifact.v2`. It has one record per
  cell (one model and one phase; four cells) under `cells`, with `floor_abs_j`, `floor_cmp_j` and
  `floor_gate_j`, and two sub-records, `absolute` and `comparative`, one per form.
  <!-- src: joulewise/detection_floor.py l.1815-1826, l.1636-1659 -->
- The dominance file of step 6, schema `joulewise.d165_dominance_closeout.v1`. Its list
  `independent_ratios` has one record per cell and form (`cell_id`, `component`), with
  `point_unguarded_floor_j`, `corner_widened_unguarded_floor_j`, `ratio` and `threshold`.
  <!-- src: joulewise/dominance_closeout.py l.46, l.215-225, l.257-270, l.283-287 -->

The point floor is read from the dominance file and from nowhere else. The floor file's own
`unguarded_floor_j` is not the point floor: the code that writes the file has already raised it to
cover the timing uncertainty.
<!-- src: joulewise/detection_floor.py l.931-965; joulewise/dominance_closeout.py l.1062-1080 -->

*Layout.* Four panels, one per cell: the two models by decode and prefill-p2048. Horizontal axis in
each: energy in joules, linear, from 0. Two rows per panel: absolute form above, comparative form
below.

*Marks, each named in the legend.* On each row, four ticks joined by a thin line, in this order:

| Tick | Legend name | File | Field |
|---|---|---|---|
| 1 | point floor | dominance file, the record of this cell and form | `point_unguarded_floor_j` |
| 2 | corner-widened floor (timing uncertainty allowed for) | the same record | `corner_widened_unguarded_floor_j` |
| 3 | after the guard for fewer than 10 kept units | floor file, this form's sub-record | `corner_widened_guarded_floor_j` |
| 4 | with the whole-window drift allowance: this form's floor | floor file, this form's sub-record | `drift_widened_guarded_floor_j` |

One vertical line per panel at the cell's `floor_gate_j`, named "this model's floor for this phase
(the larger of its two forms)". The code that checks the floor file requires `floor_abs_j` and
`floor_cmp_j` to equal the two forms' tick 4 and `floor_gate_j` to equal the larger of them; the row
that reaches the line is labelled "sets this model's floor". This line is one model's floor, not yet
the floor a contrast must exceed: that is the larger of the two models' lines for the same phase,
and it is the band B-D3 draws.
<!-- src: plan §5 l.330-333; joulewise/detection_floor.py l.1802-1822; joulewise/analysis_engine/__init__.py l.296 -->
Beside each row, as text: R (the record's `ratio`, which is tick 2 ÷ tick 1), both values in joules,
the number of kept units (`n` in the absolute sub-record, `n_blocks` in the comparative one), and
the registered words "point diagnostic; no interval": R is one computed value, and the registration
gives it no uncertainty interval. One small marker on each row at the record's `threshold` times the
point floor, named "R = 2, the registered threshold".
<!-- src: joulewise/detection_floor.py l.4128-4147; plan §6 l.344-346, l.359-360 -->

*Why ticks and not stacked bars.* The steps do not add. Tick 2 is a maximum (over the corners of the
timing uncertainty, and never below tick 1); tick 3 multiplies tick 2 by the guard; only tick 4
adds. A stacked bar would say that the floor is a sum of parts, which is false.
<!-- src: plan §5 l.303-309; joulewise/detection_floor.py l.1614-1618, l.1518-1521 -->

*Caption must carry.* That R is a point diagnostic with no interval (plan §8.1 l.566). That the two
models' floors were measured in separate windows.

*Left out.* A cell or form whose record is null or refused draws no tick and prints the file's
reason code in plain words. It is never drawn at zero.

*Open.* The wording of tick 4 depends on section 10, point 6.

### 7.2 B-D2, reported phase energy

*Question.* How much processor-rail energy did each phase of one request use, for each model, and
how wide is the interval around that number?

*Source.* One record per reported cell, schema `joulewise.paper_reported_energy_projection.v1` (step
10 of the analysis). Fields: `mean_j`, `lower_j`, `upper_j`, `per_token.j_per_token`, `n_bundles`
(the number of kept members), and the recomputation record `interval` with `n_r` (kept repeats),
`n_b` (kept quads), `h_j` and `B_j`; and `binding.attribution_floor_j`. The analysis plan registers
the `interval` record; the program that writes it does not exist yet.
<!-- src: plan §3.1 l.170; plan §4 l.273-276; plan §9 l.622-623; plan §11 l.659 -->

*What the interval is made of.* The mean m is taken over the kept units, with the repeats weighted
0.2 and the quads 0.8. The half-width h is a 95% Student-t half-width from the unit-to-unit scatter.
B covers what scatter cannot show. Every member records three bounds on its own phase energy: how
far it could move if the power records were shifted in time within the member clock bound; an
interpolation bound, which is zero for this sampler's records; and half the whole-window drift
allowance. B is the sum of the three, each averaged over the kept members with the same 0.2 and 0.8
weights. The interval runs from m − h − B to m + h + B. <!-- src: plan §4 l.224-247 -->

*Layout.* Two panels, one per phase (decode; prefill-p2048), each with its own vertical axis: gross
phase energy per request, joules, linear, from 0. In each panel two positions, the 1.7B model and
the 8B model, separated by a gap that carries the words "separate windows". No line joins the two.

*Marks, each named in the legend.* A filled circle at `mean_j`. A thick bar from m − h to m + h,
named "variation between kept units". A thin bar from `lower_j` to `upper_j`, named "with the
members' timing and drift bounds". Beside the circle, an open bracket whose half-height is
`binding.attribution_floor_j`, named "attribution floor: not part of the interval". Under each
position, as text: kept repeats of 10, kept quads of 10, the number of attempts of that window's
pack, and the energy per token (`per_token.j_per_token`: per output token for decode, per prompt
token for prefill-p2048).

*Caption must carry.* The single-window sentence (plan §8.1 l.512-514): the interval covers
variation inside one window, not between windows or days, and the independence of units is an
assumption. The separate-windows sentence (l.564-565): the two models' cells were collected in
separate windows in a fixed order, and their difference is not a comparison. The attribution-floor
sentence (plan §4 l.255-257): the timing of the phase edges alone could move the cell's energy by up
to about that many joules, which the interval does not include. The conditionality sentence (plan
§8.1 l.472-474), which says what the numbers are conditional on: a window that passed the hazard
checks at its arm and kept at least 8 of its 10 repeats and 8 of its 10 quads after the registered
removals.

*Left out.* A refused cell draws nothing and prints its refusal in plain words.

### 7.3 B-D3, the two contrasts

*Question.* On the same workload, does the 8B model use more phase energy than the 1.7B model, by
more than the instrument can produce when nothing differs?

*Source.* The file that holds each contrast's estimate and outcome, written by step 9 of the
analysis: schema `joulewise.claim_verdicts.v1`, one record per contrast. Fields:
`estimator.estimate`, `estimator.n` (kept quads), `estimator.metrology_aware_CI95` and
`deterministic_bounds.decision_interval` (each with `lower` and `upper`), `floor.active_floor_j`,
`multiplicity.adjusted_p`, `claim_evaluation.outcome`.
<!-- src: plan §3.1 l.169; plan §9 l.626, l.628; joulewise/analysis_engine/__init__.py l.185-203, l.1595-1649, l.296 -->

*Layout.* Two panels, one per contrast (decode; prefill-p2048), each with its own vertical axis:
difference in gross phase energy per request, 8B model minus 1.7B model, joules, linear, with a
labelled line at zero.

*Marks, each named in the legend.* A filled circle at the estimate. A thick bar for the metrology
interval. A thin bar for the decision interval. A shaded band from −`floor.active_floor_j` to
+`floor.active_floor_j` around zero, named "detection floor: the larger of the two models' floors".
Under each panel, as text: kept quads of 10, the Holm-adjusted p-value, and the outcome in plain
words.

*What is never drawn.* The floor band and an interval are separate things with separate jobs. No
mark is drawn at their sum, and nothing but the registered outcome word says whether a contrast is
resolved.

*Caption must carry.* The order sentence (plan §8.1 l.527-528): every quad ran 1.7B, 8B, 8B, 1.7B in
that fixed order, not randomized. The floor-transfer assumption (plan §5 l.333-337): the floors were
measured in other windows than the quads. The gross-energy sentence (plan §7.3 l.456-457): phase
energy is gross, so it includes the machine's baseline power over the phase, and where one model's
phase lasts longer, part of the difference is baseline power times the extra duration. That an
outcome of "unresolved" or "not resolvable" is not a finding of no difference.

*Left out.* A contrast that is not estimable draws no mark and prints the outcome only.

*Extra wait.* Both contrasts need all three analysed windows; they are never computed from a partial
block. <!-- src: plan §2.3 l.100-101 -->

### 7.4 B-D4, reference drift and battery temperature

*Question.* Did the instrument or the machine drift between the start and the end of each window,
how large was the allowance made for it, and did the battery keep warming during a stage? The last
part needs its reason. The cooldown between members waits on idle processor power and measures no
temperature, so heat carried from one member to the next (the registration names the members of the
8B model) is invisible to it. The battery's temperature sensor, read each time a cooldown ends,
shows whether a stage was still warming. That reading decides nothing: whether the numbers stand is
decided by the reference drift check, and the reading is kept to size the waits of later windows.
<!-- src: reg §0.6 l.369-374, l.379-381 -->

*Source.* For each analysed window:

- the harvest's `derived/neg8-screen.json` (the counts of surviving references, the formula and
  which bound was used) and `derived/neg8-allowance.json`, which names the record that carries the
  allowance: the record of the reference drift check stored with the window, or the one the harvest
  wrote when it re-ran the check on the surviving references
  (`withheld/neg8-rescreen-bracket.json`); <!-- src: reg §0.12 l.645, l.650-655 -->
- from that record, for each of the two energy families the check is run on (gross energies, and
  energies with the idle baseline subtracted): `start`, `midpoint` and `end` (each with `n`,
  `mean_j` and the individual energies `member_points_j`), `derived_repeatability_bound_j` (the
  reference drift bound for the surviving counts), `trajectory_excursion_max_j` (the spread),
  `drift_allowance_j` and `screen_passed`;
  <!-- src: joulewise/whole_window.py l.1870-1883, l.2129-2156 -->
- the flags that name a lost reference, a lost midpoint or a spare that ran;
  <!-- src: reg §0.12 l.608, l.628, l.636-639 -->
- for the contrast window's two interior references, the gross energy in each member's re-reduced
  summary: the summary the harvest recomputes from the member's stored raw files and keeps in the
  restricted part (`withheld/`) of the archive it makes of the window. No harvest output selects
  these two members by their role, and no registered disclosure prints their energies. Their marks
  are therefore labelled exploratory, the registration's word for an analysis that was not
  registered in advance (section 10, point 13);
  <!-- src: reg §0.12 l.503-508; reg §8 l.2896-2897; plan §8.1 l.541-551; joulewise/b5/harvest.py l.27-29 -->
- the battery-temperature readings taken each time a cooldown ends (`battery_temperature_readings`
  in each stage's manifest). <!-- src: reg §0.6 l.372-374, l.383-384 -->

The program that assembles these for print does not exist yet.
<!-- src: plan §8.1 l.541-559; plan §11 l.669 -->

*Layout.* One row of two panels per analysed window.

*Panel (a), reference energies.* Horizontal axis: three positions, start, midpoint and end; in the
contrast window two further positions for the interior references. Vertical axis: gross energy of
one reference request, joules. Marks: a dot for each surviving reference; a ringed dot for a spare
that ran; a cross on the axis, with its reason in plain words, for each lost reference (a lost
reference has no energy mark, because its energy enters nothing); a short horizontal tick at the
start mean and one at the end mean; a shaded band centred on the start mean whose half-height is the
reference drift bound for the surviving counts; a bracket at the right edge whose height is the
whole-window drift allowance; hollow diamonds for the contrast window's interior references, named
"exploratory: recorded only, not used by the check, not a registered disclosure". As text: surviving
counts against the planned three, one and three; the size of the corpus; pass or fail. The panel
draws the gross family and prints the decision of the idle-subtracted family as text.
<!-- src: reg §0.12 l.527-534, l.503-508 -->

*Panel (b), battery temperature.* Horizontal axis: the cooldown readings of the window in the order
taken, grouped by stage with each stage labelled. Vertical axis: battery temperature in °C. Marks: a
dot per reading, joined within a stage. A stage levels off when it has at least three readings and
its last three lie within 0.5 K of each other. A stage whose temperature rose by more than 3 K from
its first reading to its last without levelling off is labelled "rose without levelling off"; a
stage with a missing reading is labelled "not recorded". A stage of one member has no cooldown and
so no reading. <!-- src: reg §0.6 l.374-379 -->

*Caption must carry.* If the midpoint was lost, the fixed sentence of plan §8.1 l.547-549: drift
inside the window that reverted by its end was not measured, and the drift allowance uses the start
and end references only. For a stage labelled in panel (b), the fixed sentence of plan §8.1
l.556-557: the stage warmed by so many kelvin without levelling off, the window's reference drift
check passed or failed, and the reported numbers rest on that check, not on this reading. That the
battery temperature changes no number. That the interior references' marks are exploratory and not a
registered disclosure.

*Left out.* Attempts that are not the analysed window of their pack are not drawn; they are listed
in the paper's attempt history.

### 7.5 B-D5, the whole-machine cross-check

*Question.* Does the processor-rail energy of a request move with the energy entering the whole
machine, and what share of the machine's extra energy do the rails account for?

*Source.* `withheld/meter.json` in the archive the harvest makes of each analysed window: one row
per member with `rail_delta_J` (ΔE_rail), `machine.delta_J` (ΔE_machine),
`machine.battery_term_available` and `rho` (ρ). The meter's flags, whose codes begin `meter.`, are
read from the harvest's `derived/flags.jsonl`. The statistics are those of plan §8.2.
<!-- src: plan §8.2 l.577-600; joulewise/b5/harvest.py l.6113-6132 -->

*Panel (a), scatter.* Horizontal axis: ΔE_machine, joules. Vertical axis: ΔE_rail, joules. One point
per collected member, kept or removed, because the meter describes every member. Marker shape by
model, marker colour by workload. One labelled line, ΔE_rail = ΔE_machine, named "the rails cannot
exceed the machine". A member is **plausible** when 0 < ρ ≤ 1 and ΔE_machine − ΔE_rail ≥ 0; every
other member is drawn with a cross and listed by the caption. A member whose battery reading was
unavailable is drawn hollow. A member carrying any meter flag is ringed.
<!-- src: plan §8.2 l.591-593 -->

*Panel (b), the share.* One strip per model and window. Horizontal axis: ρ, from 0 to 1. Marks: a
dot per plausible member; a long tick at the median; a box from the 25th to the 75th percentile;
whiskers at the smallest and largest value. The analysis plan calls the first analysed window in
which no member carries a meter flag the first clean window. In every later window, a shaded band at
the first clean window's smallest-to-largest range for the same model, named with that window's
identifier; members outside the band stay drawn and are only counted. If no window is clean, no band
is drawn and the caption says so. As text: (largest − smallest) ÷ median, and the word "consistent"
when it is at most 0.2. <!-- src: plan §8.2 l.589-600 -->

*Caption must carry.* The boundary sentence (plan §8.2 l.610-611): whole-machine DC input plus the
battery's contribution, measured at the USB-C input, without the adapter's conversion loss. That
this cross-check enters no reported number and removes no member (l.608-609).

*Left out.* A window in which the meter recorded nothing draws nothing and says so. A member with
ΔE_machine at or below zero has no ρ and appears in panel (a) only.

### 7.6 B-D6, with and without battery-assisted members

*Question.* Do the members during which the battery helped supply the machine move a reported
number?

*Source.* The with-and-without-assist values that plan §8.1 l.483-507 registers. For each reported
cell: the reported value over the kept units, and the same calculation over the kept units less
every unit that holds an assist member, with its kept repeats and kept quads and the count of assist
members. For each contrast: the estimate and its metrology interval over the kept quads, and the
same without every quad that holds an assist member, with its count of quads. The disclosure
program, which is to write these values, does not exist yet.
<!-- src: plan §8.1 l.486-503; plan §11 l.669 -->

*Layout.* The panels and axes of B-D2 (four cells) and of B-D3 (two contrasts), one position per
cell or contrast.

*Marks, each named in the legend.* A filled circle, "with assisted members": for a cell this is the
reported value of B-D2. An open circle beside it, "without assisted members", with its kept repeats
and kept quads (or kept quads, for a contrast) as text. A thin line joining the two. For a contrast,
each circle carries its metrology interval; the open circle has no test and no outcome. Where no
kept member is an assist member, only the filled circle is drawn, with the words "no assisted
member". Where removing assisted units leaves fewer than 8 units of a kind, the open circle is still
drawn, with the registered words "below the registered minimum of 8 units" (for a contrast, "of 8
quads"). <!-- src: plan §8.1 l.493-496, l.502-503 -->

*Caption must carry.* That both values are registered, that neither was chosen after seeing the
data, and that the first is the reported one (plan §8.1 l.494-495).

## 8. Rules for every figure

1. **One field, one mark.** A mark in a data figure is one field of one issued artifact, read
   through the project's single route for paper inputs (`open_paper_input(role, runs_root)`,
   decision D-173). No figure reads a member's raw directory, and no value is retyped from prose.
   The one exception is labelled as such where it is drawn: B-D4's exploratory marks for the
   interior references (section 10, point 13). <!-- src: plan §1 l.61-62; plan §9 l.631 -->
2. **Missing is missing.** A missing, refused or inconsistent input removes the affected mark and
   prints the reason in plain words. It never becomes zero and never selects a kinder alternative.
3. **Kept units and attempts travel with the mark.** Every mark from block 5 shows its kept units
   and the number of attempts of its pack, and the caption carries the fixed conditionality sentence
   of plan §8.1 l.472-474: the numbers are conditional on a window that passed the hazard checks at
   its arm and kept at least 8 of its 10 units of each kind (section 7.2).
4. **Separate windows are never joined.** No line, shared bar or difference connects a mark from the
   1.7B window to one from the 8B window. Only the contrast window compares models.
   <!-- src: reg §1 l.881; plan §12 l.686 -->
5. **Floors and intervals keep separate jobs.** A floor is drawn as its own mark. No figure draws
   the sum of a floor and an interval as a threshold.
6. **A threshold is drawn only if it is registered.** These are: R of at least 2; the 5 ms limit on
   the member clock bound; the band 0 < ρ ≤ 1.
   <!-- src: plan §6 l.346; reg §4.2 l.1199; plan §8.2 l.591 -->
7. **A point diagnostic is labelled as one.** R carries the words "point diagnostic; no interval"
   wherever it is drawn. <!-- src: plan §6 l.359-360 -->
8. **The measurement stack is on every data figure:** machine, macOS build, runtime (the library
   that runs the model; here MLX, Apple's framework for running models on its own chips), model and
   quantization, and sampler; with the registered label of what energy the sampler covers,
   `M3 Max / MLX / powermetrics SoC rails`. In that label "SoC rails" are the processor rails of
   section 2; SoC, system on a chip, is the processor package that holds the CPU, the GPU and the
   neural engine. <!-- src: reg §1 l.887-890 -->
9. **The phase-attribution limitation is on every figure that plots a phase energy:** phase energy
   is reported without a measured check of how the instrument assigns energy to phases (decision
   D-177; plan §8.1 l.567).
10. **Captions take the weakest wording the artifact supports.** A stronger sentence names its
    evidence in the same sentence (decision D-119). Sentences the analysis plan fixes are copied by
    the analysis's disclosure program, not retyped. Captions use the plain names of section 2: no
    decision numbers, flag codes, field names or window labels.
11. **Before the release event, only synthetic.** The plotting code runs on fixtures labelled
    synthetic, watermarks every output SYNTHETIC, and refuses an input that is labelled neither
    synthetic nor released.
12. **Schematics say so.** A schematic states that it is a schematic, labels synthetic numbers
    SYNTHETIC and computed values "computed from registered constants", and names every visual
    element in the figure or in its caption. Its build script regenerates the file byte for byte,
    and a test finds each drawn element's name in the caption.
13. **A window is not a night.** No figure labels a window as a night or a day. Time axes are in
    hours from the scheduled start, and an expected length is never drawn as if it were a deadline,
    nor a deadline as if it were an expected length (section 2, "How long a window is").

## 9. What changed from the plan of 2026-09-03

The old plan specified five result figures (A to E) for a campaign that was never collected in that
form, and listed four schematics. Its figure specifications named row keys of
`docs/paper/results-fill-registry.md`. Since 2026-09-05, when Paper A was selected as a methods
paper with no campaign results (decision D-174), none of those rows may be filled.

| Old plan | Now | Why |
|---|---|---|
| Sources were fill-registry row keys | Sources are artifact schema and field, from plan §9 | The registry rows may not be filled; plan §9 fixes what is printed from which artifact |
| Model cells keyed 1.5B and 7B; "prompt processing" with no length | Qwen3-1.7B and Qwen3-8B; prefill at 2,048 prompt tokens | Block 3 chose the length; the registration fixes the models <!-- src: reg §0.5 l.331-334; reg §0.7 l.392-394 --> |
| A window with any failed member was discarded, so every mark had all its units | Marks show kept units; a window is usable with at least 8 of 10 | Ruling of 2026-10-05: a failed member costs only its own unit <!-- src: reg l.27-40; reg §6.6 l.2476-2478 --> |
| Figure A: three marks per cell (absolute, comparative, operative) | B-D1: the four steps of each form, the floor, and R | The steps are fields of the issued file, and R is the paper's question about timing |
| Figure B: mean and one interval | B-D2: mean, the two parts of the interval, the attribution floor beside it, kept units | Plan §4 registers the parts |
| Figure C: estimate, interval, floor | B-D3: estimate, both registered intervals, floor band, outcome | Plan §7 registers two intervals |
| Figure D, and Figure E's phase-consistency panels and settling (recovery-time) panel | Dropped | Their campaign was removed from the paper's scope by a decision of 2026-09-08 (D-177) and was not run; block 5's analysis plan registers no recovery-time quantity (section 4.5) |
| Figure E's drift panel, from a characterization report | B-D4: from each window's own reference members, with surviving references and spares, and battery temperature | reg §0.12; reg §0.6 |
| No figure for the battery | B-D6 | Assist is disclosed, with every number printed both ways <!-- src: reg §9.2 l.3012-3014 --> |
| No whole-machine figure | B-S2 and B-D5 | An inline meter now records the whole machine <!-- src: reg §5.8 l.2004-2007 --> |
| One schematic of the older window (Figure A2) | B-S1 | The window's shape changed: 60 s settles, spares, one calibration verdict per window <!-- src: reg §5.1 l.1536-1541 --> |
| No figure of what stops a window | B-S3 | Since the ruling of 2026-10-05 only a measured hazard refuses, and every other check is a flag <!-- src: reg l.27-36 --> |
| No rule about time | Section 8, rule 13 | The deadline, about 25 to 29 h, is easily read as the length of a window, which is about 5 to 9 h <!-- src: reg §5.5 l.1848-1852 --> |

Carried over unchanged in substance: no figure reads raw member directories; a missing input is
never drawn as zero; point diagnostics are labelled; floors and intervals keep separate jobs;
captions take the weaker wording; schematics carry no measured value.

## 10. Open points

1. **Placement.** No block-5 value has a place in a paper until the ruling of reg §14 Q4. This plan
   assigns no printed figure number.
2. **One paper or two.** Whether Paper B's sections form a new paper or succeed Paper A's sections
   is the project owner's decision. The figures are needed either way; only their numbering depends
   on it.
3. **B-R1** is held until it is ruled which values of blocks 1 to 3 may be printed (section 6).
4. **Analysis programs.** The program that issues the reported cells and the disclosure program are
   not written; B-D2, B-D4, B-D5 and B-D6 name fields the analysis plan registers, and the field
   names of records that do not exist yet may differ when the programs land (section 7.0, point 3).
5. **The attribution floor.** No file yet fixes its value for this macOS build (reg §14 Q5). Until
   one does, B-D2 draws no bracket.
6. **The whole-window drift allowance in the floor.** The code that issues the floor file adds the
   whole-window drift allowance to each form's floor (`joulewise/detection_floor.py`,
   `_add_whole_window_drift_allowance`, l.1480-1521), and B-D1's tick 4 draws that field. Plan §2.4
   (l.130-132) says that a floor's value does not use the whole-window drift allowance. The two need
   reconciling before B-D1's caption is written; this plan changes neither.
7. **A second with-and-without comparison.** Plan §8.1 l.475-482 proposes, and does not yet adopt,
   recomputing each number without the exclusions for physical conditions during a member. If it is
   adopted it gets marks of the same form as B-D6.
8. **B-S1's second panel** (the block as three windows back to back) is recommended here and was not
   asked of the figure's builder.
9. **Slot ids.** Once `docs/paper/paper-b/slots.json` is committed, each mark in section 7 gets the
   id of the slot that names its schema and field.
10. **After the seal.** Every `src:` comment in this file is rechecked against the sealed text, and
    the line numbers are refreshed. Values that `docs/paper/paper-b/registered-values.json` carries
    (a table generated from the same files) are checked against it.
11. **Figure A2 and Figure P1.** Figure A2 shows the window as designed before block 5; Paper A is
    merged and keeps it. Figure P1 belongs to the protocol document, which predates the block-5
    registration and is to be brought into line with it separately; whether Figure P1 changes is
    decided there.
12. **Terms for the lexicon.** This plan defines these terms itself, because the lexicon did not
    build them when this plan was written: mark, class, state, artifact, schema, field, slot,
    expected length, deadline, capture, kept unit, point floor, corner-widened floor, guard,
    metrology interval, decision interval, the four outcomes of a contrast, assist member, ΔE_rail,
    ΔE_machine, ρ, plausible, and disclosure program. If the lexicon builds any of them under
    another name, this plan takes that name.
13. **The interior references in B-D4.** The registration records the contrast window's two interior
    references as a measure of drift inside each half of the window (reg §0.12 l.503-508). The
    reference-drift disclosure of plan §8.1 (l.541-551) does not list their energies, and neither
    does the list of what the disclosure program must write (plan §11 l.669). An analysis that is
    not registered is labelled exploratory (reg §8 l.2896-2897), so B-D4 draws these two marks with
    that label, from each member's re-reduced summary. Printing them as a registered disclosure
    needs one line in plan §8.1 and one in the disclosure program's list; without those lines the
    marks stay exploratory or are dropped.
