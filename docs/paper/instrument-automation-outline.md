# Outline: the instrumentation and automation paper

**Status.** Section-by-section outline, written 2026-10-21 (PDT) by Opus 5.5 (an AI model session) for Ed, the
project's owner. It was revised after six rounds of checks of its wording, each by AI model sessions that had no part
in writing it (two separate checks of the whole file in the fourth round; the fifth and sixth each confirmed the
fixes before them and checked the changed lines), which ask whether every term is built before it is first used, and
after a re-check of its numbers against their sources. On 22 October, §6 and §12 took in the battery reading's
reporting delay (how long after the battery's energy flows its reading is recorded), measured for a later written
decision (a *ruling*, BAT-2) on how to count the battery's energy in another experiment on this instrument (§0 item
18). It is not a draft of the paper's prose and has not been sent to anyone; whether any of it goes to the advisor
(the academic supervising the work, to whom the paper would go) is Ed's decision.

**Why it exists.** Ed, 2026-10-20: "seems we're close to an instrument paper, whatever the first paper is i forget if
joules per request matches up in disag inference as you'd expect by model size" (his mail, transcribed in
`docs/process_traces/2026-10-20-magistrate-c634f6f3/RECORD.md:21-23`; "disag inference" is his shorthand for
disaggregated inference, in which a request's two parts, reading the prompt and writing the answer, are handled and
measured separately). The plan of 2026-10-14 names the first paper: *Paper A by mid-November: method plus
replication* (`docs/design/block6_collection_draft.md:576` on the branch `integration/2026-10-14-b6-stage1`). This
outline is that paper, built around what the instrument (the sampler, meters and programs that measure the machine's
power; §0 item 3) and its automation have already shown. The *replication* is block 6, the re-run of the three
measurement plans on later days (§0 item 16). Its numbers are blinded (read by no person or AI tool) until the
*release*, the dated, written entry in the project's records after which they may be read (§0 item 28). Ed's question
about model size is one of the results that wait for the release, so every section below says whether it can be
written now or waits for the release.

**What this outline never contains.** No energy, power or phase duration (a *phase* is one of a request's two parts,
reading the prompt or writing the answer; §0 item 4), and none of the three quantities computed from them (a *floor*,
the smallest energy difference the method can tell from noise; a *contrast*, the energy difference between the two
compared models; an *outcome word*, the registered verdict on a contrast; all built in §0 item 27), from the two data
collections whose numbers the paper's results rest on (the *claim collections*): 8-12 October (block 5) and 17-21
October (block 6). Every joule and watt printed here comes from a non-claim session (one collection run of several
hours whose numbers never enter the paper's results): the quiet-machine measurements of 16-17 October, the rehearsals
of 6 and 9 October, or the check session of 21 October (the three kinds are built in §0 item 18), or from a synthetic
example. Each is labelled where it appears. This outline sets no threshold: no level at which a check passes or
fails, which is called a *cut-off* below. Every cut-off it quotes is cited to the place that records its derivation
or its size in joules, and where no record gives one, the outline says so (item 5 of the list "Open decisions for Ed"
at the end of this outline).

**How to read a section.** Each paper section below has the same parts: the *forcing problem* (why the mechanism must
exist), the *claim* the section makes, the *evidence* (file and line), the *status* (writable now, or waits for the
release), a *worked example* with real numbers, and the *figures*, with every visual element named. A citation `:N`
or `:N-M` after a file name means line N, or lines N to M, of that file; "registration `:188`" is line 188 of the
registration (§0 item 5). Repository paths are at `origin/main` `ef520743c` unless another commit or branch is named,
and paths under `/Users/edr/` are local files on the measurement Mac, outside the repository.

---

## 0. Words used, in the order they are needed

Each term is built here before any section uses it. A term used in only one section is built in that section, before
its first use.

1. **The machine.** One Apple MacBook Pro with an M3 Max chip (model identifier Mac15,9), dedicated to this work. Its
   140 W Apple power adapter plugs into the mains and feeds it through a cable from the adapter's USB-C socket to the
   laptop's MagSafe charging port.
2. **Rails.** The chip's own power sensors report the electrical power of three on-chip parts: the general-purpose
   processor cores (CPU), the graphics processor (GPU) and the neural engine (ANE, a block for neural-network
   arithmetic). Their sum, *rail power*, is the quantity every result of the paper measures.
3. **Power record.** macOS's built-in sampling tool, `powermetrics` (the *sampler*), is asked for one reading every
   100 ms and in fact delivers one about every 130.5 ms. Each reading, a *power record*, is the *average* rail power
   over its own time span; inside that span the power is known only as that average. The sampler reports each
   record's length, and each record starts where the one before it ended, so once the end of the first record is
   placed on a clock (§3's *clock anchor*), every record's start and end follow: the k-th record ends at that time
   plus the lengths of records 2 to k (draft-v2 `:1130`; *draft-v2* is the project's earlier methods draft,
   `docs/paper/draft-v2-skeleton.md`). The *instrument* is everything that turns a request into a printed energy: the
   sampler, two further power readers (a USB-C meter on the adapter's output and the laptop's own battery-current
   sensor, items 12 and 13), a short timing-calibration run at each session's start and end (item 11), and the
   programs that place the readings on the request's clock and sum them. The machine (item 1) is what the instrument
   measures.
4. **Request, prefill, decode, phase, edge, workload.** One *request* asks a language model to continue a prompt. A
   *token* is one of the word-pieces a language model reads and writes (a word, part of a word, a digit); prompts and
   answers are counted in them. The model first reads the whole prompt and computes the first output token
   (*prefill*), then produces the remaining output tokens one at a time (*decode*). Prefill and decode are the
   request's two *phases*; the program running the model writes a timestamp at the start and end of each, the phase's
   two *edges*. A *workload* is the fixed prompt and output length a request uses. A request's energy is its prefill
   energy plus its decode energy.
5. **Registration.** The document, written and reviewed before any data exists, that fixes the measurement plan, the
   arithmetic and the rules for which data are removed; *registered* means fixed there. It is
   `docs/registrations/block6_replication_DRAFT.md`, cited below as "registration" with its line numbers.
6. **Phase energy.** Each power record contributes its average power times the time it overlaps the phase. *Example
   (synthetic, registration §1.3):* a phase runs from 10.00 s to 10.25 s; a record over 9.90-10.03 s at 20 W overlaps
   it for 0.03 s and gives 0.60 J; a record over 10.03-10.16 s at 30 W gives 3.90 J; a record over 10.16-10.29 s at
   30 W overlaps 0.09 s and gives 2.70 J; phase energy 7.20 J. Nothing is subtracted for idle power: the energy is
   *gross* (registration `:138-139`). This sum is called the *overlap sum* below. *Figure 0: the overlap sum.* x axis
   time (s) from 9.90 to 10.30; y axis power (W). Three grey rectangles, one per power record, each as wide as its
   span and as tall as its average power (9.90-10.03 s at 20 W, 10.03-10.16 s at 30 W, 10.16-10.29 s at 30 W); two
   vertical solid lines labelled "phase start 10.00 s" and "phase end 10.25 s"; the part of each rectangle between
   the two lines hatched and labelled with its joules (0.60, 3.90 and 2.70 J); caption "phase energy = sum of the
   hatched areas = 7.20 J (synthetic)".
7. **Run, runner, stage.** A *run* is one request measured in its own process: about 75 s of *idle baseline* (the
   machine doing nothing, recorded to check that it is quiet), one unmeasured warm-up request, then the measured
   request. The program that does this and stamps the phases is the *runner*. Two workloads are measured: a *decode
   workload* (a 42-token prompt and 512 output tokens), whose decode phase is reported, and a *prefill workload* (a
   2,048-token prompt), whose prefill phase is reported. A *stage* is one ordered list of runs executed together, for
   example ten runs of the decode workload in a row.
8. **Repeat, quad, unit, cell.** A *repeat* is one run on its own. A *quad* is four consecutive runs in the order A,
   B, B, A, where A and B are the quad's two *sides*: when two models are compared, the two models; otherwise the
   same model and workload on both sides (a *null quad*, whose A-minus-B difference can only come from the instrument
   and the machine). If each run reads a little more than the one before (a slow, steady drift), the two A runs and
   the two B runs carry the same total drift, so A minus B is free of it. A *unit* is one repeat or one quad, the
   draw the statistics treat as independent; removing one run of a quad removes the whole quad. A *cell* is one
   reported energy per model and phase.
9. **Pack, session, t0, chain, attempt, round.** A *pack* is one measurement plan, fixed before collection: ALPHA
   measures the model Qwen3-1.7B, BETA the model Qwen3-8B, GAMMA compares the two. A *session* is one unattended
   collection of a whole pack, 125 runs for ALPHA and BETA and 107 for GAMMA, about five hours; its runs fall in a
   decode half and then a prefill half. *t0* is the moment the session's *driver* starts: the session's top-level
   program, which checks the physical state of the machine, starts the monitoring programs and then runs the *chain*,
   the script that runs the session's stages in order. An *attempt* is one try at a session. A *round* gives each
   pack at most one attempt, in an order that moves on by one pack each round (ALPHA, BETA, GAMMA; then BETA, GAMMA,
   ALPHA; then GAMMA, ALPHA, BETA; and so on); a pack that is held (item 26) or already has its target of three
   sessions that count (item 23) is skipped that round, which is why block 6 has a round 4 (§7). Block-6 sessions are
   named round-then-pack: *r1-alpha* is round 1's ALPHA session.
10. **Reference runs, drift screen.** *Reference runs* use a fixed third model (Qwen2.5-1.5B, 1,024-token prompt, 256
    output tokens) at fixed places in every session: 18 at the start, a group of 3 right after them, 1 at the
    midpoint (between the decode half and the prefill half) and 3 at the end. Their energies are never reported as
    results; they exist only to check the instrument. The *drift screen* passes when the end references read the same
    as the start references within the references' own run-to-run scatter, so the instrument did not drift during the
    session.
11. **Calibration capture.** A short run at a session's start and another at its end in which the GPU is switched on
    and off on command, so that the timing between the sampler's records and the runner's stamps can be measured (§3
    builds it).
12. **USB-C meter and DC input.** A USB-C power meter (ChargerLab POWER-Z KM003C) is plugged into the adapter's USB-C
    socket and the cable to the laptop is plugged into the meter, so every watt the adapter delivers passes through
    it; a second USB-C cable carries its readings to the Mac. The project's records call it the *wall meter*, but it
    sits on the adapter's DC output, not at the mains socket. It reads voltage and current 50 times a second. Their
    product is the *DC input*: the power the machine takes from the adapter. The adapter's own loss in turning mains
    AC into DC happens before the meter and is in no number; the cable's own small loss happens after the meter and
    is counted as machine power. (This order of adapter, meter, cable and laptop is taken from session notes and
    awaits Ed's confirmation at the machine: item 6 of "Open decisions for Ed".)
13. **Battery current.** The laptop's System Management Controller (SMC, the chip that runs the laptop's battery
    charging circuit and its power sensors) reports the battery's current once a second; a negative value means the
    battery is discharging into the machine.
14. **Battery assist.** A moment when the battery discharges while the adapter is attached, because the machine needs
    more power than the adapter delivers.
15. **Agent, census.** An *agent* is an AI coding assistant process (Claude Code or Codex) running on the machine.
    Agents measured in rehearsals drew 8 to 47 W while "idle" (registration `:188`), so none may be alive while
    anything that counts is measured. The *census* is a scan for agent processes every 30 s.
16. **Block, usable.** A *block* is a set of sessions collected under one plan fixed in advance. Block 5 (8-12
    October 2026) gave one *usable* session per pack (one whose data entered block 5's results; block 6's word for
    the same status is *counting*, item 23). Block 6 (17-21 October) repeated the three packs to test whether block
    5's numbers hold on other days: the *replication*.
17. **Ed.** The project's owner, who runs the machine and can stop any session.
18. **Non-claim sessions used here.** A *non-claim* session is one whose numbers never enter the paper's results. The
    *quiet-machine kit*: 11 measurements, each carrying an M-number from M1 to M15 (the numbering has gaps; only the
    numbers used below are cited), taken 16-17 October with no agent alive, over 51,524 s of wall time, to measure
    the quantities from which the rules' cut-offs are drawn
    (`docs/process_traces/2026-10-17-magistrate-1a1261a5/RECORD.md:6`). The *rehearsals*: four non-claim sessions of
    6 and 9 October, run with the collection code but outside any result; their 77 runs (53 of them on 9 October) are
    the data on which §5 tries every proposed exclusion rule. *Session H*: a check session of 21 October for BYTES, a
    separate experiment on the same instrument, not yet registered, which asks whether a model's decode energy per
    token follows the bytes it reads from memory per token. It ran models up to 122 billion parameters, in a *check*
    stage (five requests per model) and a *soak* stage (the same 70-billion-parameter request repeated back to back),
    and was stopped by Ed at 17:19 PDT (`RUN_STATE.md:233-234`).
19. **Physical hazard.** A state of the machine that would make a measured energy wrong if collection ran through it:
    running on battery or charging; the clock being jumped by a correction (*stepping*) or running at the wrong rate
    (*clock drift*, not the slow change in the instrument's readings that item 10's drift screen checks); thermal
    pressure (macOS reports it as a *thermal level*, an integer that is 0 when the system applies no thermal limit);
    another process using the processor (*contention*; such processes, other than the measurement's own, are *outside
    processes*); too little free disk; the sampler slow or not sampling; the machine sleeping; an agent alive.
20. **Refusal, flag, exclusion.** A *refusal* stops collection or removes data; §5 names the only grounds on which
    one may happen. A *flag* is a recorded fact written beside the data (a code such as `sleep.in_run`, the run or
    session it concerns, the observed value and the evidence); it removes nothing by itself. An *exclusion* is what
    the registration says a given flag does: remove the run, remove the session, or only disclose. The *flag catalog*
    is the file listing every flag code and its effect.
21. **Labelled alternative, known-good, replay.** Where a rule could reasonably have been drawn another way, the
    paper prints the registered result and, beside it, a *labelled alternative* computed under the other rule.
    *Known-good* data are non-claim sessions whose recorded values nobody disputes (the rehearsals and the
    quiet-machine kit of item 18). An agent was alive throughout every rehearsal; the one alive on 9 October used 2
    to 3% of one processor core, §5 finds no trace of it in the rehearsal's energies, and the quiet-machine kit,
    taken with no agent alive, replaced the rehearsals' values wherever it measured the same quantity (registration
    `:886-890`). A proposed rule is *replayed* on known-good data (applied to their stored records to count how many
    runs it would remove), and a rule that removes known-good data is suspect.
22. **Harvest, desk.** After a session ends, the *harvest* program reads its raw files, re-derives every check from
    the preserved bytes, writes every flag, applies the registration and writes the *verdicts* (its written decisions
    on whether each run and session counts). The *desk* step is the harvest plus compressing the raw files; it runs
    with no measurement in progress.
23. **Counting session, line.** A *counting session* is one that no physical hazard stopped and that carries no
    session-excluding flag; only counting sessions enter the registered numbers. A *line*, in this outline, is one
    printed row of results: the *flagged-inclusive line* is a labelled alternative printed beside each registered
    result, with the non-counting sessions added back where they can be computed.
24. **Pinned commit.** The one version of the collection code, named by its git commit hash, that a block's sessions
    run from, in a separate copy of the repository used for nothing else (block 6: `f31aca19f` for all nine
    sessions). A reviewed change to that code during a block is pinned again by a dated addendum to the registration
    (registration `:529-535`).
25. **Pre-session check, smoke, machine test.** The *pre-session check* (*pre-check* below) measures the physical
    hazards directly (no model runs) before a session may start. A program's *launch route* is how it is started: by
    hand, or by a job of macOS's job scheduler (`launchd`) whose declared job type (`ProcessType`) sets the priority
    of everything it starts. A *smoke* is a short real collection (4 to 6 runs) of the same pack by the same code, on
    the same launch route as the session (the same `launchd` job and job type, not by hand), judged by the desk
    programs before the session. A *machine test* is a 40-minute live test of the pinned commit that injects faults
    (an agent appearing, a disturbed idle baseline, the meter unplugged) and checks that each leaves its expected
    record.
26. **Loop, orchestrator, arming, hold.** The *loop* is a set of plain programs that macOS's job scheduler
    (`launchd`) starts every few minutes; it runs pre-check, smoke, session and desk, session after session, with no
    agent alive. The *orchestrator* is the AI model session that leads the project; it runs only between sessions,
    when the loop wakes it or a person starts it. *Arming* a session is committing to start it: at the end of a
    passing pre-check the loop sends Ed a notice, and the session starts no sooner than 30 minutes later (the *NO
    window*), and only if he has not answered NO (§7). A *hold* stops the loop from arming a pack (or any pack) until
    the orchestrator has looked; a *stop file*, a marker whose presence holds the loop, is how a person holds it by
    hand.
27. **Floors, contrast, outcome word.** A *detection floor* is the smallest energy difference the method can tell
    apart from noise. It is computed from one pack session's kept runs: from the spread of the repeats around their
    mean (its *absolute* form) or from the A-minus-B differences of the null quads (its *comparative* form), as the
    larger of the largest single deviation and a prediction t × s × √(1 + 1/n) (s the deviations' standard deviation,
    n their count, t the 95% Student-t multiplier), widened by letting each value move within its own timing
    uncertainty (§3) and multiplied by a *guard factor* g(n) that widens the floor when n is small: √(9 / (n − 1))
    for n from 5 to 9, and 1 from n = 10; below n = 5 it is undefined, so no floor is computed and the cell is not
    printed (registration `:933-958`, `:579`; its synthetic example: n = 9 repeats, g = 1.0607, give a floor of
    0.5765 J). An *attribution floor* is the largest timing bound (§3: the energy a run's phase edges can move under
    the session's timing error) over a cell's kept runs; it is printed beside the cell, because every run is placed
    on the clock by the same method, so it does not shrink when runs are averaged (registration `:215-217`). A
    *contrast* is GAMMA's 1.7B-versus-8B energy difference on the same workload; it is judged against the larger of
    the two models' detection floors (the *floor gate*), each model's floor coming from its own pack's session. An
    *outcome word* is the registered verdict on a contrast, one of four, tested in this order: `not_estimable` (an
    input is missing or invalid); `not_resolvable` (chiefly: the difference is no larger than the floor gate);
    `unresolved` (chiefly: its statistical interval contains zero); otherwise `direction_supported`, whose direction
    is the difference's sign (the full conditions: registration `:990-993`).
28. **Blinding, release.** Until the *release*, no person or AI tool reads a block-5 or block-6 energy, power, phase
    duration, floor, contrast or outcome word; programs compute them into restricted files. *Structure* (verdicts,
    counts of flags and runs, hazard readings, stage timing that is not a phase duration) is not restricted
    (registration §12.1, `:1124-1138`). The release is a dated, written entry in the project's records after which
    the numbers may be read.

---

## Front matter (writable now)

**Working titles.** (a) *An unattended, physics-gated energy instrument for language-model inference on one laptop*;
(b) *Measuring the energy of language-model inference on Apple Silicon without anyone watching: an instrument, its
rules, and a blinded replication*.

**Abstract (structure only until the release).** One paragraph: the problem (a software power sampler on a personal
laptop, many processes and clocks that can corrupt a phase energy, and a single session that cannot show whether a
number holds on another day); the instrument (rails, a USB-C meter on the adapter's output and the battery current,
with in-session timing calibration); the rule set (collection stops or data are removed only for a directly measured
physical hazard or where no number of the registered experiment would exist; every other condition is a recorded
flag; every excluding rule's cut-off set in joules and replayed on known-good data before adoption); the automation
(a loop with no person or agent on the machine collected 9 of 9 counting replication sessions, 1,071 of 1,071 planned
runs, in 78 hours); the blinded replication, with an independent recompute (a second program, sharing no code with
the analysis, that recomputes the numbers from the raw records; results at release). The sentence with the
replication's numbers is a placeholder until the release.

**Contributions** (each is a section below): an instrument with three independent views of power (§2) and timing
calibration inside every session (§3); direct measurement of every physical hazard (§4); a rule set that refuses only
on measured physics or where no number of the registered experiment would exist, and sets every exclusion's cut-off
in joules (§5); a measured answer to battery assist (§6); an unattended loop and its record (§7); live tests that
found defects before data was lost (§8); blinding with an independent recompute (§9); a record of how the software
was built and checked (§10); the replication (§11).

---

## 1. Introduction

- **Forcing problem.** Energy per phase of a language-model request is a small number measured on a machine that is
  never fully idle: system daemons wake on their own, the clock can be corrected under the program, the machine can
  sleep, and the people and AI tools that build the software run on the same machine. In block 5, rules about
  bookkeeping files rather than about the machine's physical state cost most of the machine time (a list of the runs
  the drift screen, §0 item 10, needed, which a program failed to write; a calibration acceptance file, §3, older
  than the latest capture it should have listed): BETA spent 42.5 h of wall time for one usable 5.9 h session, 21.4 h
  of it in five lost attempts and 15.1 h in the gaps between them; three of the five losses were rule losses, two of
  them certain before t0 from files already on disk.
- **Claim.** A single laptop can measure phase energy unattended, session after session, if (i) power is read three
  independent ways, (ii) the two clocks (the sampler's and the runner's) are calibrated inside every session, (iii)
  collection stops only for a directly measured physical hazard or for data that cannot be the registered experiment,
  and everything else is written down and decided by a rule fixed in advance, and (iv) no agent is alive and nobody
  uses the machine while it measures. Block 6 is the test of that claim.
- **Evidence.** `docs/design/block6_collection_draft.md:42-44` and `:66-78` (block 5's losses, table by attempt;
  integration branch); `RUN_STATE.md:203` (block 6 tally); `/Users/edr/night-b6/loop/attempts.jsonl` records 1-9 (one
  structure line per block-6 session).
- **Status.** Writable now, except the last paragraph, which states the replication's result at release.
- **Worked example (structure, real).** Block 5's BETA: attempts a1 to a6, chain run-times of 6.05, 2.53, 0.13, 6.95,
  5.77 and 5.92 h; only a6 usable; lost chain time 6.05 + 2.53 + 0.13 + 6.95 + 5.77 = 21.4 h; wall time from a1's t0
  to a6's end 42.5 h. Block 6: 9 sessions, 9 counting, first t0 17 October 20:51 PDT, the loop reached its final
  state, DONE (every pack at its target of three counting sessions; §7), 21 October 02:54 PDT (78.1 h), 46.4 h of it
  collecting.
- **Figures.** *Figure 1: one usable session against nine.* Two horizontal time bars on a shared axis, "hours since
  the bar's first t0", from 0 to 80. Upper bar, "block 5, BETA pack": six segments, one per attempt (a1 to a6), each
  as long as its chain, coloured "lost: bookkeeping rule" (a1, a4, a5), "lost: physics" (a2, an agent opened at the
  keyboard), "lost: the start-of-session calibration capture measured a delay above a fixed cut-off (§3)" (a3) or
  "usable" (a6), with the gaps between them in grey and labelled "reviews and rule changes between attempts". Lower
  bar, "block 6, all packs": nine segments coloured by pack (ALPHA, BETA, GAMMA), each labelled with its session name
  (r1-alpha ... r4-alpha, round then pack), with the desk step after each in a lighter shade of the same colour and
  the time from one desk step's end to the next t0 (pre-check, smoke, the NO window of §7) in grey, labelled "between
  sessions". A legend names every colour. No energy appears.

## 2. The machine and three views of its power

- **Forcing problem.** The rails see only the chip. A reader, especially one who builds whole-system energy
  benchmarks, asks what the whole machine pays, and whether the rails miss power the workload causes elsewhere
  (memory, storage, fans, voltage regulators). One sensor cannot answer either question.
- **Claim.** The instrument reads power at three places on one power path, each with its own clock and rate: the
  rails (`powermetrics`, one average about every 130.5 ms), the DC input (the USB-C meter, 50 samples a second) and
  the battery current (the SMC, once a second). The rails are the quantity every result rests on. A printed
  *whole-machine line*, which never enters a result, gives the DC input energy over each phase; beside it, per
  request, the *battery term* (the energy the battery discharges into the machine: its current times its voltage,
  summed over the request's time). Block 6 keeps the battery term per request, not per phase, because the battery is
  read only once a second and no reading falls inside 38% of prefill phases; a phase whose request shows the battery
  helping is flagged (§6). The ratio of rail power to whole-machine power is measured, not assumed, and depends on
  the workload.
- **Evidence.** Registration `docs/registrations/block6_replication_DRAFT.md:104-110` (machine and sampler),
  `:824-837` (the meter excludes nothing; the cross-checks M14, known loads switched on and off, and M10, a fit over
  steady load levels, both in worked example 1), `:1030-1037` (whole-machine energy per phase and its *boundary
  sentence*: the one sentence stating where the measured machine begins and ends, that is, which losses are inside
  the number and which outside); `joulewise/hazards/smc.py:17-27` (SMC keys: `B0AC` battery current, `B0AV` battery
  voltage, `PDTR` DC-in power, `PSTR` system total power); `joulewise/external/km003c_parse.py:79` (the accepted band
  around 28 V, the supply voltage the adapter and laptop agree on over USB-C; §6), `:368` (`integrate`), `:397`
  (`delta_machine_energy`); `docs/process_traces/2026-09-23-interactive-7ec32e8b/01-owner-session-record.md:100` (the
  meter placed inline on the adapter's output, its data cable to the Mac). Session H files (local): the harvest's
  meter record `/Users/edr/night-bytes/h-20261021T185555Z/archive/withheld/meter.json` (per run: the request window,
  the span from the runner's prefill-start stamp to its decode-end stamp; meter and battery energy from
  `delta_machine_energy`), the meter stream `.../custody/hazards/meter/stream-001.jsonl`, and each run's
  `.../runs-parent/runs_bytes_mac_check/*/summary_metrics.json` (`gross_energy_j`: item 6's gross phase energy summed
  over both phases; the runner also records an idle-subtracted value, which is not used here).
- **Status.** Writable now from non-claim data. The whole-machine lines of blocks 5 and 6 wait for the release.
- **Worked example 1 (quiet-machine kit M14, real).** A known load is switched on between idle stretches and seen at
  both places. A GPU load busy for 20% of each short cycle (20% *duty*) raised the meter's reading over idle by 20.15
  W and the rails' by 7.65 W, so the rails see 0.380 of the step. One CPU core at 100% raised them by 9.41 W and 5.42
  W, 0.576. Over steady load levels (M10), where each reading is the whole power, not a rise over idle, the fit is
  meter = 2.650 × rails + 1.632 W. So a load the rails see as 1 W shows as about 1.7 to 2.8 W at the meter, and the
  meter sees every tested load the rails see (registration `:830-837`).
- **Worked example 2 (session H, real; recomputed for this outline from the harvest's records).** Three clocks are
  involved. The runner stamps its prefill start and decode end on the Mac's *monotonic clock* (Python's
  `time.monotonic_ns`, which never jumps when the time of day is corrected); those two stamps bound the *request
  window*. The meter stamps its samples with its own device clock. The Mac asks the meter for new samples five times
  a second (a *poll*); each reply, a *batch*, carries the samples taken since the previous poll. The program that
  reads the meter's stream (`km003c_parse`) fits the meter's clock to a second Mac clock, its *hardware counter*
  (`CLOCK_MONOTONIC_RAW`, which nothing adjusts), by `clock_fit`. Each batch gives one point: its last sample's
  device time against the hardware-counter time at which the Mac received it. Only replies that held fewer than 63
  samples (the most one reply can hold) and came back within 3 ms of their poll are used (when at least 20 replies
  do; with fewer, every reply is used). A least-squares straight line is fitted through those points; the device time
  is cut into 10 s stretches, the point in each stretch lying furthest below that line (the earliest arrival) is
  kept, and the final line is the least-squares line through the kept points alone, because a delivery delay can only
  make a batch late. The meter stream also records the difference between the monotonic clock and the hardware
  counter at its start and at its end; the two readings must agree within 1 ms (they differ only across a sleep), and
  a runner stamp plus that difference is a hardware-counter time (`raw_offset_ns`). Each poll's reply also carries
  the SMC's battery current and voltage as read at that moment (the SMC refreshes them about once a second); the
  battery energies in this outline come from those embedded reads. Meter energy (`integrate`): the mean of the
  samples inside the window times the window's length. Rail energy: the run's request energy as item 6 defines it,
  gross, prefill plus decode (`gross_energy_j`), so nothing is subtracted from either side, as nothing was from the
  steady levels M10 was fitted on.
  - The meter's clock on session H: the fit used 93,525 of the stream's 93,532 batches (those that met both
    conditions); the meter's clock and the hardware counter differ in rate by 12.6 ppm; batches arrived a median 5.8
    ms after the final line (95th percentile 14.9 ms), and the earliest lay at most 6.7 ms before it. A sample's
    placement is thus uncertain by a few milliseconds, under a third of the 20 ms between samples. The difference
    between the monotonic clock and the hardware counter read −0.5 µs at the stream's start and −6.8 µs at its end.
  - Qwen3.5-122B-A10B (4-bit), 2,048-token prompt and 512 output tokens, run r01: 15.734 s; rails 507.7 J, a mean of
    32.269 W; meter 1,340.2 J, 85.18 W. M10 predicts 2.650 × 32.269 + 1.632 = 87.14 W, 2.3% above the measured 85.18
    W.
  - Llama-3.3-70B-Instruct (4-bit), same workload, soak-stage run r01: 82.573 s; rails 3,124.0 J, 37.833 W; meter
    9,017.1 J, 109.20 W. M10 predicts 101.89 W, 6.7% below the measured value; over the 11 soak runs the shortfall is
    5.1% to 10.9%.
  - Reading: the rails' share of the machine (rails over DC input plus battery) is workload-dependent (0.377 to 0.379
    for the five 122B requests, 0.330 to 0.352 for the eleven 70B soak requests), so the paper prints the measured
    DC-input line and never converts rails into machine power with M10.
- **Figures.** *Figure 2: the power path and the three taps.* A left-to-right block diagram. Boxes, in order: "mains
  socket"; "140 W adapter (AC to DC; its loss is upstream of every printed number)"; "KM003C meter in the adapter's
  USB-C socket, tap M: DC input voltage × current, 50 samples a second"; "USB-C-to-MagSafe cable (its loss is counted
  as machine power)"; "laptop power input"; a branch to "battery, tap B: SMC battery current × voltage, once a
  second, negative = discharging"; then "system-on-chip, tap R: CPU, GPU and ANE rails, one average every ~130.5 ms"
  and "rest of the machine: memory, storage, fans, regulators, display circuitry (seen only at M)". Solid arrows are
  power flow, labelled "adapter power" and "battery power"; dashed arrows from each tap to a box "recorded streams",
  each dashed arrow labelled with its clock (meter: its device clock, fitted to the Mac's hardware counter; SMC: each
  read carried in a meter poll's reply and stamped with that reply's arrival on the hardware counter; power records:
  labelled by the sampler with whole wall-clock seconds and placed on the request's clock by each run's *clock
  anchor*, its own fit of its records to wall time, built in §3). *Figure 2b: the meter's clock fit.* x axis meter
  device time (s); y axis "arrival time minus final line (ms)". Small dots: every batch used; filled dots: the
  earliest batch in each 10 s stretch, through which the final line is fitted; a solid horizontal line at 0, the
  final line; a dashed line, the first least-squares line through all used batches; a bracket from 0 up to a typical
  dot, labelled "delivery delay". *Figure 3: rails against DC input.* Main panel: rail power (W) on x and meter power
  (W) on y, both as whole power (not rises over idle); the solid line is the M10 fit with its equation printed on it,
  and open squares are session H's request means (labelled with model and run). Inset: the M14 load steps as filled
  circles, each plotted as the rise the load caused over idle on both axes (labelled "GPU 5% duty", "GPU 20% duty",
  "one core"), with a dotted line through zero at M10's slope, 2.650, for comparison. A note under the plot says
  every point is non-claim.

## 3. Placing power records on the request's clock

- **Forcing problem.** Power records are stamped by the sampler; phase edges are stamped by the runner. Before a
  record can be shared between phases, the two time bases must sit on one timeline, and any error in that placement
  moves energy across the phase edge. Repetition cannot remove it: every run of a session is placed by the same
  method.
- **Claim.** The sampler labels each power record only with the whole second of wall time (`CLOCK_REALTIME`) in which
  it ended, while the runner stamps phase edges on the Mac's monotonic clock (§2). Each run therefore fits its own
  *clock anchor* (draft-v2 `:155`; the inequalities are in its Appendix A.3.3). The runner reads the wall clock five
  times during the run, each reading taken between two readings of the monotonic clock. The anchor keeps every
  straight line from monotonic time to wall time (a rate and an intercept), together with every value of A, the wall
  time at which the sampler's first record ended, that fits all the evidence: each wall reading lies between the
  line's values at its two monotonic readings; each record's end (A plus the lengths of the later records up to it,
  §0 item 3) falls inside the whole second its label names; and the first record starts after the sampler was
  launched and is read only after it was written. Half the range of the A values kept, plus the small fixed
  allowances that draft-v2 `:155` lists, is the run's *clock bound* m, the most the whole trace can be misplaced on
  wall time; s_run is the change in wall-minus-monotonic time over the run's sampler stream. The resulting placement
  of records against the phase edges is the *alignment*, and each session measures its error, end to end, twice, with
  a *calibration capture* at its start and another at its end.

  A capture drives the GPU through 59 commanded one-second on/off pulses. For each pulse, the capture's fitting
  program (the *estimator*) fits the power records near the pulse (every record overlapping the time from 0.75 s
  before the on command to 0.75 s after the off command) with a rectangle whose rise and fall may each be shifted,
  early or late, from the commanded times. The rectangle's prediction for a record is the resting power (the median
  of the records taken between pulses) plus the pulse height (the median of the records lying wholly inside the
  pulse's flat top, at least 0.25 s from either command, minus the resting power) times the fraction of the record's
  span the shifted pulse covers. The *fit loss* is the sum, over those records, of ρ((y − ŷ)/σ), where y is a
  record's average, ŷ its prediction, σ the larger of 0.001 W and 1.4826 times the median distance of the
  between-pulse records from the resting power (a stand-in for their standard deviation that one outlying record
  cannot inflate), and ρ Huber's function (x²/2 for |x| ≤ 1.345, 1.345 × (|x| − 0.6725) beyond). A pair of shifts
  (onset, offset) is *consistent* when its loss is at most the *loss cut-off*, the best pair's loss plus the larger
  of 1.0 and 5% of it; the set of such pairs, widened by the small uncertainty of the command stamps, is the
  *accepted region* (draft-v2 `:1158-1160`, `:1164-1172`, `:1194-1196`, `:1209`). The capture's *fiducial bound* is
  the largest absolute shift, onset or offset, in the accepted regions of all 59 pulses, plus the capture's own clock
  bound (the m of its own clock anchor, found as for a run; draft-v2 `:1220-1222`): the largest timing error between
  a commanded and an observed edge that the records allow.

  The session's *operative timing bound* is b_op = max(opening, closing) + max(|closing − opening|, s_bracket), where
  *opening* and *closing* are the fiducial bounds of the start and end captures and s_bracket allows for the
  alignment moving between the two captures: the range of fiducial bounds over a set of captures on the quiet
  machine, or a fixed minimum if that is larger (worked example below). Every phase edge of a run is then moved, on
  its own, by up to b_op + s_run, while the whole power trace is shifted by up to ± m; the largest change in phase
  energy is the run's *timing bound*, one of the recorded bounds added together to give its uncertainty (registration
  `:207-214`; worked example below).
- **Evidence.** Registration `:191-217` (captures, b_op, and how the bound enters each run's uncertainty), `:361-401`
  (the calibration acceptance file, built in the worked example below, and its constants), `:1214-1221` (M1 and M13
  values); `docs/paper/draft-v2-skeleton.md:125-173` (the full capture algorithm, already written: pulse schedule,
  fit, accepted region, the clock anchor, and the *bracket*, the pair of captures between which every run of the
  session sits); draft-v2 `:1158-1160` (the records near a pulse and the pulse height), `:1164-1172` (the loss),
  `:1194-1196` (the loss cut-off and the accepted region), `:1220-1222` (the fiducial bound), `:1305-1348` (one real
  pulse worked through, Table A3), `:551` (that capture's bounds); registration `:856` (the clock-rate measurement
  M3); `configs/calibration/calibration_acceptance_d079_v2.json:470-480` (the origin of the 10.818 ms minimum).
- **Status.** Mechanism writable now (reuse draft-v2 §2 and Appendix A.3). Block 6's own capture values and b_op are
  restricted until the release.
- **Worked example (real, non-claim).**
  - *One pulse, worked (a July capture, before both claim collections; draft-v2 Table A3).* Twenty-two records of
    about 120 ms around one commanded one-second pulse (the capture's tenth); resting power 0 W, σ at its 0.001 W
    minimum, pulse height 42.55 W. The best shifts are +27 ms at onset (late) and −7 ms at offset (early), with a
    loss of 13,724.3 against 478,338.5 for no pulse at all; the loss cut-off is 13,724.3 + max(1.0, 0.05 × 13,724.3)
    = 14,410.5, and every pair of shifts at or below it belongs to the accepted region. Widened for the command
    stamps, that region runs from 25.45 to 28.93 ms at onset and from −8.61 to −5.31 ms at offset (draft-v2 Figure
    A6), so this pulse's largest absolute shift is 28.93 ms. It is the largest of the capture's 118 edges, and adding
    the capture's clock bound, 1.13 ms, gives its fiducial bound, 30.07 ms (draft-v2 `:551`).
  - *The acceptance constants for block 6.* The *calibration acceptance* is the file that fixes, before any session,
    the constants used to judge captures. For block 6, 13 captures on the quiet machine (10 from M1, a set of
    captures taken for this purpose, and 3 from M13, the meter timing check below) had fiducial bounds from 27.38 to
    37.05 ms; their range is 9.675 ms, below the 10.818 ms minimum (the range of fiducial bounds in the first
    calibration acceptance's set of quiet captures, August 2026, 10.817749 ms rounded to the microsecond, and kept as
    the minimum since), so s_bracket = 10.818 ms. The largest value, 37.05 ms, became the *alignment reference*: a
    capture above it is flagged, never refused. The one timing stop is on b_op itself: an ALPHA or GAMMA session
    stops when b_op exceeds 139 ms, because at that bound the timing bound of the pack's smallest phase, the
    Qwen3-1.7B prefill, reaches a quarter of that phase's energy (0.25 × 26.1 J = 6.5 J, at 0.047 J per ms of edge
    movement; rehearsal sizes), and a run whose timing bound exceeds a quarter of its phase energy fails its phase
    checks, so no such run could count (registration `:346-349`, `:575`).
  - *b_op on real sessions.* Over the four non-claim rehearsal sessions, the block-6 rule gives b_op of 41.3, 41.4
    and 51.0 ms. The fourth (6 October) was stopped at its opening capture, 48.0 ms, by block 5's rule, under which a
    capture above block 5's alignment reference (36.46 ms) stopped the session; block 6 made that a flag. For it only
    the opening capture's bound plus s_bracket can be computed: 48.0 + 10.818 = 58.8 ms, far below 139 ms
    (registration `:386-389`; `docs/design/block6_collection_draft.md:90-92`).
  - *The timing bound in joules (synthetic, registration `:207-214`).* b_op = 45.6 ms and s_run = 0.4 ms move each
    edge by up to 46 ms; m = 2 ms; the record holding the start edge averages 40 W and the one holding the end edge
    10 W. Moving the start edge 46 ms earlier and the end edge 46 ms later adds 0.046 × (40 + 10) = 2.30 J; shifting
    the whole trace a further 2 ms adds 0.002 × (40 − 10) = 0.06 J. The run's timing bound is 2.36 J.
  - *A check that shares nothing with the capture.* M13 timed the same commanded on and off transitions at the USB-C
    meter: the meter's transitions lag the commands by 31.2 ms on average and lag the sampler's by 25.2 ms (standard
    deviation 4.7 ms over 354 transitions), so the sampler's own transitions lag the commands by about 6.0 ms
    (standard deviation 11.4 ms), inside the 30 ms typical capture bound.
  - *The clocks themselves.* M3 read wall time (`CLOCK_REALTIME`) against a hardware counter nothing adjusts
    (`CLOCK_MONOTONIC_RAW`) 5,147 times, 10 s apart, over 51,514 s with automatic network time off: the slope is
    −4.67 × 10⁻⁷ ppm (standard error 5.19 × 10⁻⁷ ppm). Over the longest stretch across which one run's clock readings
    are taken (335 s) that moves a run's clock by 1.6 × 10⁻¹⁰ s.
- **Figures.** *Figure 4: one calibration pulse.* x axis time (ms), y axis GPU power (W). Elements: the commanded
  pulse as a dashed rectangle between "command on" and "command off" (two vertical dashed lines); the power records
  as horizontal solid bars, each spanning its record's interval at its average power (labelled "one power record,
  ~120 ms"); the fitted rectangle, its rise and fall shifted from the commands, as a solid outline; two horizontal
  arrows "onset shift +27 ms" and "offset shift −7 ms" between commanded and fitted transitions; a shaded band
  "accepted shifts" around each fitted transition (25.45 to 28.93 ms at onset, −8.61 to −5.31 ms at offset). Data:
  the worked pulse above (draft-v2 Table A3, July, non-claim). *Figure 5: the bracket.* A session timeline (left to
  right) with two short blocks "opening capture" and "closing capture" at its ends; above each, a vertical bar whose
  height against a y axis "fiducial bound (ms)" is that capture's bound; a brace joining them labelled "b_op = larger
  bound + max(difference, s_bracket)"; a phase-edge inset (x axis time, y axis power) showing a phase edge moved by
  ±(b_op + s_run) and, separately, the whole trace shifted by ±m, with the energy that moves across the edge hatched.
  Values in the figure are the registration's synthetic example recomputed with block 6's s_bracket (opening 40.0 ms,
  closing 30.0 ms: b_op = 40.0 + max(10.0, 10.818) = 50.818 ms), labelled synthetic.

## 4. Measuring the machine's state directly

- **Forcing problem.** Every hazard of §0 item 19 has a cheap proxy (a settings string, a *receipt file* that a
  program writes to record that a step ran, a job's declared priority), and proxies can say "fine" while the physics
  is not. Block 5 lost sessions to proxies, and its rehearsals ran with the agent census's stop overridden every
  time, so the code that stops a session when an agent appears was never exercised before it stopped block 5's BETA
  attempt a2 (§1).
- **Claim.** Every hazard is measured as the physical quantity itself, by a monitor that runs beside every session at
  fixed cadences (clock every 1 s, battery current every 1 s, thermal level every 5 s, processor time of outside
  processes every 10 s, free disk every 60 s) and by the pre-session check before t0. The pre-session check's
  cut-offs: adapter attached with battery current within 200 mA of zero and the battery not charging; OS thermal
  level 0; 180 s with no outside process above 5% of one core; no agent alive; free disk at least the largest
  session's measured writes plus 20 GiB (43 + 20 = 63 GiB); the sampler's median interval at most 150 ms over 300
  records; model files equal to the hashes recorded for them before the block. A failed reading waits and is measured
  again; it never becomes a guess.
- **Evidence.** `joulewise/hazards/monitor.py:17-41` (cadence table); registration `:860-873` (pre-t0 rows, taken
  from block 5 and the design; two further pre-check readings that are flags rather than refusals, each with its
  derivation: a single interval above 200 ms among the sampler's 300 records, and keyboard or mouse input within the
  last 600 s); the sizes of the taken-over cut-offs in `docs/design/next_block_threshold_proportion.md:137` (5% of
  one core: 0.19 J on a 0.62 s prefill), `:141` (thermal level 0), `:142` (200 mA: 2.4 W at the battery, outside the
  rails) and `:149` (disk: a low-disk reading can add no energy to any run, so its cut-off needs no size in joules);
  registration `:338-343` (when the census sees an agent, the chain lets the run in flight end, pauses, and resumes
  10 minutes after the last sighting; the driver keeps the machine from sleeping and checks at every run's start and
  end that it did not sleep); `RUN_STATE.md:133-134` and
  `docs/process_traces/2026-10-17-magistrate-6789ef94/RECORD.md:5-19` (the media daemon of worked example 1 below);
  `RUN_STATE.md:138-139` and `docs/process_traces/2026-10-17-magistrate-f4db0072/RECORD.md:9-26` (the launch route);
  `docs/design/block6_collection_draft.md:90-94` (block 5's rehearsals overrode the census) and `:70` (BETA a2).
- **Status.** Writable now. Hazard readings are structure, not restricted.
- **Worked example 1: a daemon that would have contaminated every run (17 October, pre-checks of the first block-6
  session, real).** The pre-check refused twice on contention (another process using the processor): "no 180 s run of
  clean 30 s intervals within 600 s; last dirty interval: mediaanalysisd at 1.856 CPU-s/s" (a "run" in this message
  is an unbroken stretch of intervals, not a measured run of §0 item 7; an interval is *clean* when no outside
  process used more than 5% of one core in it, *dirty* otherwise) and 1.907 on the second try (CPU-seconds used per
  second of wall time: about 1.9 cores kept busy), against a cut-off of 0.05 CPU-s/s (`mediaanalysisd` is Apple's
  photo and video analysis daemon, which works when the machine is idle on AC power, exactly the loop's own
  condition). The polite stop signal (SIGTERM) was ignored for 30 s; the forced kill (SIGKILL) made `launchd` restart
  it within 5 s at 178-199% CPU; the pause signal (SIGSTOP) held it at 0.0% CPU, after which the busiest process was
  the loop itself at 1.4%.
- **Worked example 2: a launch route that slowed the sampler (17 October, real).** The sampler check refused on all
  five pre-checks, numbered 000001 to 000005 by the loop, including the three that passed the contention check after
  the media daemon was held: 237, 178, 197, 183 and 180 records of the 300 required within 55 s, median intervals
  218, 298, 259, 290 and 299 ms against the 150 ms cut-off. The same probe gave 300 records at a 131 ms median in
  both machine tests that day. The cause: the loop's `launchd` job was declared `ProcessType Background`, which
  throttles its children, `powermetrics` included. The job was reloaded declared `Interactive` (the reload stopped
  pre-check 000006 before it finished), and the next pre-check, 000007, captured 300 of 300 records over 39 s, a mean
  interval of 130 ms. Nothing had been collected, so no number was affected.
- **Worked example 3: why one slow interval is only a flag (real, non-claim).** In 101 non-overlapping 300-record
  windows of quiet idle baselines, none holds an interval above 200 ms (the largest is 166.8 ms); the 150 ms median
  cut-off already refuses the slow launch route, and the pre-check's sampler probe (its 300 records) enters no
  reported energy, so a slow interval there can change no number.
- **Figures.** *Figure 6: the sampler under two launch routes.* Strip plot, x axis "pre-check, as the loop numbers
  them" (000001 to 000007, each labelled with its start time, 18:10 to 19:22 PDT), y axis "interval between power
  records (ms)"; filled circles for the medians of the five Background checks (000001 and 000002 also marked "refused
  on contention too", worked example 1); at 000006 a cross labelled "stopped by the reload, no reading"; at 000007 an
  open square for the first Interactive check's mean, labelled "mean; Interactive"; a horizontal dashed line "refusal
  cut-off 150 ms" and a dotted line "nominal 130.5 ms"; each marker labelled with its record count out of 300.
  *Figure 7: the monitor's cadences.* A timeline of one minute with one row per hazard log file (*journal*: clock,
  battery, thermal, contention, disk), each tick a reading, labelled with its interval.

## 5. Physics refuses; everything else is a flag

- **Forcing problem.** A rule that removes data can bias a result as surely as a contaminated run can, and a rule
  whose cut-off is drawn without a size in joules can remove known-good data for nothing. Block 5 removed sessions
  for bookkeeping conditions (a list of runs that a program failed to write, a calibration acceptance file older than
  the latest capture; §1) that no measurement showed had changed a number.
- **Claim.** Collection stops, or data are removed, on one of five grounds only, and the registration names the
  ground beside every rule: **P**, a directly measured physical hazard, which includes a contamination flag (built in
  the worked example) whose measured added energy reaches the registered size; **N**, the number is undefined (an
  input the arithmetic needs is missing, or too few runs remain for it to exist); **W**, the data are not of the
  registered model, runtime (the software that runs the model) or code; **D**, the registered drift screen fails;
  **S**, the collection code failed structurally: the chain crashed, a stage with planned runs left none of their
  records while later stages ran, or the capture records or the list of runs are missing. P is the "physics" of this
  section's title; N, W, D and S are the least without which there is no number of the registered experiment to
  print. Everything else is a flag, printed. Each excluding rule that is new or changed in block 6 must meet five
  requirements before adoption: it is replayed over every known-good non-claim archive and its removal count written
  beside it; its cut-off is set by the energy it can add, in joules, against F_min, the smallest floor the paper
  prints (built in the worked example below); anything it can know before t0 is computed before t0 by the same
  function; it is applied in the analysis to a session collected in full, not by stopping collection; and it is
  rehearsed on full-size data. Of block 5's 32 session-removing codes, 25 are flags in block 6.
- **Evidence.** Registration `:553-567` (the rule and its four non-physical grounds), `:569-600` (session exclusions
  table, each row with its ground), `:593` (25 of 32), `:684-704` (the sizing formula and F_min), `:711-713` (the
  three contamination flags), `:735-747` and `:769-799` (the outside-processor rule, its measurement and its replay),
  `:724-727` and `:843-844` (the graphics rule), `:627-630` (the 5 ms clock rule), `:841-848` (worked example with
  rehearsal sizes), `:877-897` (the five requirements, and the agent rule's replay at `:879-882`);
  `docs/process/pruning_list_2026-10-14.md` (the inventory of checks it was applied to).
- **Status.** Writable now.
- **Worked example (real, non-claim).** (A *contamination flag* records energy that something other than the run's
  own workload may have added: another process, another program on the GPU, a long disturbed wait before the run.)
  - *The size every exclusion is drawn at.* F_min is the smallest floor of either kind (§0 item 27) the paper prints,
    estimated from non-claim data: the decode attribution floor of Qwen3-1.7B, 45.7 ms of operative timing bound
    (that of block 3, a collection before the claim collections) times 0.041 J per ms of edge movement (the slope
    measured on the 9 October rehearsal) = 1.9 J; the rehearsal's other floors were at or above it (registration
    `:697-704`). A contamination flag excludes a run when the energy it can have added to the run's phase reaches
    F_min / 4 = 0.475 J. The registration states this quarter but records no derivation for the factor. What it does
    record is the size of the choice: no registered decision changes for any F_min from 0.73 to 2.6 J, that is for a
    cut-off anywhere from 0.18 to 0.65 J (registration `:704`; the registration ruling
    `docs/process_traces/2026-10-17-magistrate-52d50d1f/reg-ruling-opus.md:83-90`). For scale, a 5-unit mean's
    statistical half-width (half the width of its 95% interval) on the same rehearsal is 0.47 J (threshold note
    `docs/design/next_block_threshold_proportion.md:292-304`). The paper needs one sentence of derivation (item 5 of
    "Open decisions for Ed").
  - *A rule kept as physics, although its replay removes everything.* An agent at its lowest measured draw, 8 W, over
    a 0.62 s prefill (rehearsal size) adds 8 × 0.62 = 4.96 J, ten times 0.475 J, so the whole unit an agent overlaps
    is removed. Replayed literally on the rehearsals, the rule removes all 77 runs (53 of 53 on 9 October, 24 of 24
    on 6 October), because an agent was alive in every rehearsal (§0 item 21). It is kept because an agent is a
    physical hazard counted directly by the census, not an estimate of added energy; the rehearsals stand only as
    non-claim sizing at that load (registration `:879-882`).
  - *A rule adopted after its replay.* Another program on the GPU: the added energy is P_x × T_phase, where P_x is
    the GPU-plus-ANE rail power in the run's idle baseline and T_phase the length of the run's measured phase, so the
    cut-off is P_x = 0.475 J / T_phase: 0.77 W for a 0.62 s Qwen3-1.7B prefill and 0.24 W for a 1.99 s decode
    (rehearsal sizes). The quiet machine's own GPU-plus-ANE power was 0.2 mW median and 1.3 mW at most over the 53
    baselines of 9 October, and the rule removes 0 of the 77 rehearsal runs (registration `:724-727`, `:843-844`).
  - *A rule that fails its replay and stays a flag.* Outside processor work: M4 measured w = 5.432 J per CPU-second
    (the largest of 20 bursts of one busy core at interactive priority, the priority of programs a person is using),
    and the quiet machine's own resting processor use by outside processes is c_q = 0.54 CPU-s per 10 s interval. The
    rule "exclude when 5.432 × (C − k × 0.54) ≥ 0.475 J" (C the outside CPU-seconds in the k intervals the request
    overlaps) draws its cut-off at 0.0874 CPU-s of excess, about a fifth of the quiet machine's own 10th-percentile
    interval (0.41 CPU-s). Replayed on the 53 known-good rehearsal runs of 9 October, it removes 14, and 38 of
    all 77. On the same session's reference runs, phase energy regressed on outside CPU gives −0.09 ± 0.09 J per
    CPU-second at prefill; two reference runs with about 20 outside CPU-seconds read 11.11 and 11.44 J at prefill
    against their 23 siblings' 11.26 ± 0.38 J, where the rule predicts 104 and 107 J added. So the rule is a recorded
    flag, and each cell prints the rule's result beside it as a labelled alternative. M4's steady load at *background
    priority* (the low priority at which macOS runs its own daemons) costs w = 0.0862 J per CPU-second, 63 times
    less; with that w the rule still removes 2 of the 53 and 14 of the 77, so it is printed only as a second labelled
    alternative (registration `:788-792`).
  - *A rule kept from block 5.* A run whose own clock anchor (§3) allows more than 5 ms of misplacement is removed: 5
    ms is 0.21 J at one edge of a 42 W prefill, and the rule removes 1 of the 77 rehearsal runs, one whose clock fit
    was unresolved, so it would have been removed anyway (registration `:627-630`).
- **Figures.** *Figure 8: the decision path of one condition.* A flow chart. Diamond "measured physical hazard
  (ground P)?"; "yes" leads to a box "refuse on ground P: wait and re-measure before t0, stop the session, or remove
  the run"; "no" leads to a second diamond "ground N, W, D or S?", whose "yes" leads to a box "refuse on that ground:
  remove the run or session, naming the ground, and print the flagged-inclusive line" and whose "no" leads to a box
  "write a flag (code, run, observed value, evidence)", then a third diamond "named as excluding in the
  registration?" with "yes" to "exclude run or session, and print the flagged-inclusive line" and "no" to "disclose
  only". A side panel lists the five requirements as five ticked boxes beside the third diamond. *Figure 9: a replay
  table as a figure.* One row per candidate rule: agent overlap; outside processor at w = 5.432; outside processor at
  the background-priority w = 0.0862; another program on the GPU; a run's clock anchor allowing more than 5 ms. For
  each row, two bars, "known-good runs removed" out of 53 (the 9 October rehearsal) and out of 77 (all rehearsal
  runs), a column "size in J at the cut-off" (4.96 J for the agent at 8 W, 0.475 J for the three contamination rules,
  0.21 J for the clock rule), and a column "decision" reading "kept as physics", "kept as flag", "second labelled
  alternative", "adopted" or "kept from block 5".

## 6. The battery and the adapter's ceiling

- **Forcing problem.** The USB-C meter sits on the DC input. If the machine needs more than the adapter can deliver,
  the battery supplies the rest, and a whole-machine number read from the meter alone is too small. Was this a real
  effect on this machine, and if so, how large?
- **Claim.** Yes, on the heaviest workload. With Llama-3.3-70B the DC input reached a hard ceiling of about 136.5 W,
  consistent with a 5 A current limit at the 28 V supply voltage the adapter and laptop negotiate over USB-C (their
  *power contract*), and the battery covered the excess for a few seconds per request, almost all of it while the
  model read the prompt (prefill) and during the unmeasured warm-up request. The battery's share of each 70B
  request's energy was 0.09% to 0.29% over all 16 such requests. The rails, the quantity every result rests on, are
  not affected: they are the chip's own sensors and report on-chip power whatever its source (a physical argument,
  not a measurement). The opposite failure, losing the adapter, is a physical hazard: in block 5 the adapter's output
  lost voltage for 26 s during BETA's attempt 4 and the Mac then slept for 3,507 s, costing 4 runs, which is why the
  pre-session check and every run read the battery current directly. The whole-machine line adds the battery term
  back over each request (DC input energy + battery energy); block 6 keeps the battery term per request, not per
  phase (§2), and flags a phase whose request shows battery assist. BYTES, the other experiment on this instrument
  (§0 item 18), splits the battery term at the phase edges, and there a second problem appears: because a battery
  reading is recorded up to 2.302 s after its energy flows (worked example, second bullet), the battery energy
  recorded in the 2.302 s after a phase edge may belong to the phase before it. Its per-phase battery term carries
  that energy as uncertainty, the rule the BAT-2 ruling adopted for BYTES. In block 6 no run showed battery assist
  (Status, below).
- **Evidence.** `RUN_STATE.md:36` and `docs/design/block6_collection_draft.md:72` (the block-5 drop in the adapter's
  output); `joulewise/external/km003c_parse.py:312` (`battery_watts`: −B0AC × B0AV / 10⁶ W at each poll), `:397-425`
  (`delta_machine_energy`: the machine term is the meter term plus the battery term); `joulewise/hazards/smc.py:1-12`
  (why the SMC key is read: the battery values macOS publishes in its device registry refresh only every 60 s and
  missed discharge bursts entirely), `:21` (`B0AC`); registration `:620-625` (charging or loss of AC excludes a run;
  battery discharge alone, `battery.assist`, is disclosed), `:860-861` (pre-t0: battery current within 200 mA of
  zero, not charging), `:1016` (the battery-assist labelled line: each estimate also over the units with no
  battery-assisted run), `:1030-1037` (whole-machine line; boundary sentence "DC input at the USB-C port; the
  adapter's AC-to-DC loss is not included"). Session H files (local): the harvest's meter record
  `.../archive/withheld/meter.json` (per run: request window, meter and battery energy from `delta_machine_energy`),
  `.../custody/hazards/meter/stream-001.jsonl` (93,535 records, one per line),
  `.../custody/hazards/monitor/battery.jsonl` (19,023 records; the hazard monitor's own once-a-second SMC journal,
  separate from the reads embedded in the meter stream, §2), and the run folders `bytes-mac-check-soak-llama-70b-r01`
  to `-r11`, `bytes-mac-check-check-llama-70b-r01` to `-r05` and `bytes-mac-check-check-qwen35-122b-r01` to `-r05`.
  The values below were recomputed for this outline from those files, except the few that the list "Check run before
  delivery" at the end of this outline names as taken from the BAT-1 and BAT-2 records cited next; a tracked script
  for the paper is still to be written. The battery-assist audit (BAT-1) on branch
  `lane/2026-10-22-battery-assist-audit` (`7e59b54ab`),
  `docs/process_traces/2026-10-22-forward/BAT-1-BATTERY-ASSIST.md:19-21` (where in the request the battery helped)
  and `:26` (no block-6 run had any battery help); it integrates the monitor's journal instead of the reads embedded
  in the meter stream (§2), so its per-run joules differ from those below by up to 0.85 J, inside its own agreement
  bar for the two paths (one second of the run's largest discharge power, 5.0 to 6.4 J on 70B). The same branch, now
  at `fc7548a17`, adds the BAT-2 ruling, `docs/process_traces/2026-10-22-forward/BAT-RULING.md:125-162` (how late a
  battery reading arrives, measured on session H: the once-a-second refresh of the reading, the gap between polls,
  the longest stretch of consecutive late discharge readings (2.13 s) and the 2.302 s bound, all built in the worked
  example's second bullet below) and `:54-56` (the battery joules recorded in the 122B requests' decode are the
  battery's discharge during prefill, reported late), and BAT-1's table of where in each request those joules sit,
  recomputed after the BAT-2 ruling from the meter stream's embedded reads (the same path as the values below),
  `docs/process_traces/2026-10-22-forward/BAT-1-BATTERY-ASSIST.md:114-123` at `fc7548a17` (with `:95` there: the gap
  between the warm-up and the measured request read no discharge).
- **Status.** Writable now from session H (non-claim). Block 6's count of battery-assisted runs is a flag count,
  which the registration treats as structure, not restricted (`:1130`): zero in all nine sessions (BAT-1 record).
- **Worked example (session H, 21 October, real).**
  - The meter's 935,345 samples over the session never exceed 136.79 W; the largest current is 4.991 A, and every
    sample at 4.95 A or more reads a supply (USB-C bus) voltage of 27.38 to 27.43 V. In all 16 check and soak
    requests of the 70B model, the largest 50 Hz sample is 136.3 to 136.4 W.
  - The battery reading arrives late. Block 6 keeps the battery term per request (registration `:1030-1037`); BYTES
    splits the battery's energy at the phase edges like the rails' energy (§0 item 6; BAT-2 ruling, Evidence above),
    but a battery reading is not stamped at the moment its energy flows. Three delays, which add, put it later. (1)
    The SMC refreshes the battery current and voltage it reports about once a second (§2), and each refreshed value
    is the average over the second before the refresh (it shows at the end of each discharge, where the last reading
    is a fraction of the one before, as a partial average would be: on one 122B check request, −76 mA and then −14
    mA), so energy that flowed at the start of that second is first reported up to 1.0 s after it flowed. (2) The
    value then stands as the reported value until the next refresh, a second later, and the battery energy is
    computed by the same rule as the meter's (§2, `integrate`: the mean of the polls' values inside the window times
    the window's length), so the value is charged at every poll that carries it, up to 1.0 s more. (3) The stream
    records a new value only at its next poll, up to one gap between polls after the refresh; on session H the
    largest gap was 0.302 s. Battery energy is therefore recorded up to 1.0 + 1.0 + 0.302 = 2.302 s after it flows,
    and never before. Check on session H: the battery supplies power only while the DC input sits at the adapter's
    ceiling (the claim above), so once the meter's power fell at the start of each 122B decode the battery had
    stopped, and every discharge reading after that fall is a late one; those readings went on for up to 2.13 s,
    inside the bound.
  - Soak run r01 (2,048-token prompt, 512 output tokens, 82.573 s): DC input 9,017.1 J; battery 9.05 J; machine
    9,017.1 + 9.05 = 9,026.1 J; rails 3,124.0 J (0.346 of the machine). Three of the 83 reads of the monitor's
    once-a-second SMC journal inside the request, taken 2 to 4 s after the request started, showed the battery
    discharging; by the reporting delay built in the bullet above, that energy flowed in the request's first 4 s, in
    its prefill. The deepest read was −395 mA at 12.758 V, 0.395 × 12.758 = 5.04 W from the battery, while the SMC's
    own DC-in reading was 129.6 W and its system total 134.2 W.
  - Over the 11 soak requests (81.6 to 84.3 s each): battery 9.05 to 26.90 J per request, 0.100% to 0.292% of the
    request's machine energy (8,874.5 to 9,361.2 J). Over the five Qwen3.5-122B check requests (15.7 s each): 1.07 to
    1.49 J, 0.080% to 0.110%. In the Qwen3-1.7B check requests of the same session the battery never discharged.
  - So the meter alone would have under-read the 70B requests by at most 0.29%; adding the battery term removes that.
    The term's own resolution is one SMC reading per second, which the paper states as a limit.
  - The delay can change a request's total battery energy only through discharge in the 2.302 s before the request
    starts (recorded inside the request) or in the request's own last 2.302 s (recorded after it). Neither happened
    in any of the session's 95 measured requests: in the 2.302 s before each start the meter read at most 14.7 W, and
    in each request's last 2.302 s at most 121.5 W, both below the ceiling; no poll in the 2.302 s before a start or
    after an end showed discharge. Split by phase, the delay does move energy across the edge between prefill and
    decode: the five 122B check requests record 1.07 to 1.49 J of battery energy each, of which 0.78 to 1.15 J is
    recorded in decode, all of it by polls received within the first 1.93 s after the edge (BAT-1's table), although
    in decode the meter never read above 92.0 W, far below the adapter's ceiling. That energy is the battery's
    discharge during prefill, while the model read the prompt, reported late. So a per-phase battery term must carry,
    as uncertainty, the battery energy recorded in the 2.302 s after each phase edge, the rule the BAT-2 ruling
    adopted.
- **Figures.** *Figure 10: one 70B request at the ceiling.* x axis time within the request (s), with a vertical
  dashed line "prefill ends" at 26.6 s. Upper panel, y axis power (W): a thin line "DC input (meter, 50 Hz)", a
  horizontal dotted line "adapter ceiling ≈ 136.5 W", and a stepped line "rails (one value per power record)". Lower
  panel, y axis battery power (W): bars, one per read of the monitor's once-a-second SMC journal (the reads of the
  worked example's third bullet), "battery → machine" above zero and "charging" below, with the three discharging
  seconds labelled with their current in mA; each bar sits at the second its reading was recorded, up to 2.302 s
  after the energy flowed (§6's worked example, second bullet), and a shaded band 2.302 s wide to the right of
  "prefill ends", labelled "reporting delay: readings here may belong to prefill", marks the readings the delay can
  move across the edge. A caption box gives the four energies of the request (DC input, battery, machine, rails), the
  battery's from the reads embedded in the meter stream, as in the worked example. *Figure 10b: why a battery reading
  is late.* One time axis (s). Bottom row: a short shaded block "energy flows". Above it, three segments laid end to
  end from the block's start: a bracket "the SMC averages the second before its refresh (up to 1.0 s)", a flat
  segment "the value stands until the next refresh (up to 1.0 s)", and a segment ending at a row of tick marks
  "stream polls", the longest gap between ticks labelled "up to 0.302 s". An arrow from the block's start to the last
  tick, labelled "recorded up to 2.302 s later, never earlier".

## 7. The unattended loop

- **Forcing problem.** An agent alive on the machine can add 8 to 47 W (§0 item 15), and a person at the keyboard is
  a disturbance too, yet a replication needs many sessions of about five hours (§0 item 9) back to back. The work
  between sessions (pre-checks, smokes, harvests, decisions) must happen without anyone on the machine while it
  measures.
- **Claim.** A loop of plain programs under `launchd` runs the whole cycle with no person or agent on the machine. It
  chooses the next pack in the rotating order of rounds (§0 item 9) and runs the pre-check. At the end of a passing
  pre-check it sends Ed a notice that the session will start no sooner than 30 minutes later (arming it, §0 item 26);
  those 30 minutes are the NO window, in which he can answer NO. The smoke and its desk check start at once, so the
  NO window runs during them (in block 6 a smoke ran before every session). When the window has closed and the smoke
  has passed, the loop checks for a NO or a stop file, measures the pre-check's hazards again and starts the session
  (t0); after the session it runs the desk step, then reviews each pack's record (a pack whose last two attempts both
  failed for the same cause is held; one that has used its allowed attempts is *paused*, held in the same way under
  its own name) and chooses again. A physical hazard makes it wait and re-measure every 240 s; a failed smoke holds
  only that pack, any other non-physical problem holds the loop, and both wake the orchestrator. Block 6 ran 9
  sessions with 9 counting and no physical stop.
- **Evidence.** `joulewise/b6/loop.py` at the pinned commit `f31aca19f`: `:285` (`_precheck`), `:308-310` (the notice
  and its 1,800 s NO window, which runs during the smoke), `:314-316` (wait and re-measure every 240 s), `:423`
  (`_smoke_desk`), `:471-473` (`_arm_wait`: nothing starts before the NO window has closed), `:564`
  (`_session_desk`), `:587` (`_rotate`), `:195-199` (`DONE`); `joulewise/b6/queue.py` at `f31aca19f`: `:26-30` (the
  rotating order), `:97` (the next round), `:125-143` (the review after each session); `configs/b6/loop.json` at
  `f31aca19f` (base order ALPHA, BETA, GAMMA); registration `:186-189` and `:466-481` (rounds);
  `/Users/edr/night-b6/loop/attempts.jsonl` records 1-9 and `/Users/edr/night-b6/loop/state.json` (`since` = the DONE
  time); `docs/process_traces/2026-10-20-magistrate-c634f6f3/RECORD.md:31-41`; `RUN_STATE.md:202-203`.
- **Status.** Writable now (all structure).
- **Worked example (structure, real).** Block 6, from the loop's ledger (its own record of every attempt). A run is
  *present* when its folder of raw files is on disk, and *succeeded* when the runner recorded its status as succeeded
  (the harvest's counts, `joulewise/b5/harvest.py:7195-7214` at `f31aca19f`):

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
  planned runs present and succeeded (the harvest's run exclusions by flag are structure counts, not restricted under
  §0 item 28; the paper's table will print them, and this outline does not transcribe them). Before each start a
  smoke ran: its collection took 21.4 to 26.4 min, and its start preceded the session's t0 by 47.5 to 76.1 min (file
  times of the smoke folders). ALPHA's round-2 session never ran: its smoke held the pack (§8), so ALPHA's third
  session moved to round 4.
- **Figures.** *Figure 11: the loop's states.* A state diagram. Nodes: NEXT (choose the next pack), PRECHECK,
  WAIT_PHYSICS (a hazard: re-measure every 240 s), SMOKE_RUN, SMOKE_DESK, ARM_WAIT (wait for the NO window to close),
  SESSION_RUN, SESSION_DESK, ROTATE (review each pack's record: hold, or pause, a pack), DONE (every pack at its
  target of three counting sessions), HOLD_LOOP (a non-physical problem, Ed's NO, or a stop file, §0 item 26: wake
  the orchestrator). Arrows, each labelled with its condition: NEXT → PRECHECK "pack chosen"; NEXT → DONE "every pack
  at its target"; PRECHECK, SMOKE_DESK, ARM_WAIT, or SMOKE_RUN or SESSION_RUN at its launch → WAIT_PHYSICS "hazard
  measured"; WAIT_PHYSICS → "hazard clear" back to PRECHECK (for a hazard found there), to SMOKE_RUN for a new smoke
  (for one found at the smoke's launch or by its desk check), or to ARM_WAIT (for one found there or at the session's
  launch); PRECHECK → SMOKE_RUN "pass: notice sent, NO window opens"; SMOKE_RUN → SMOKE_DESK "smoke ended";
  SMOKE_DESK → ARM_WAIT "smoke pass"; SMOKE_DESK → NEXT "smoke non-physical failure: hold this pack"; ARM_WAIT →
  HOLD_LOOP "NO or stop file"; ARM_WAIT → SESSION_RUN "window closed, no NO, hazards clear"; ARM_WAIT → SMOKE_RUN
  "machine or code changed since the smoke"; SESSION_RUN → SESSION_DESK "chain exit"; SESSION_DESK → ROTATE "harvest
  written"; SESSION_DESK → HOLD_LOOP "structural defect"; ROTATE → NEXT. The two collecting states, SMOKE_RUN and
  SESSION_RUN, are drawn with a heavy border and the note "no agent alive". *Figure 12: the block-6 timeline* (the
  lower bar of Figure 1 expanded): one row per session on a clock-time axis from 17 October 20:00 to 21 October
  03:00; in each row, segments for the smoke (hatched), the NO window (outline only, overlapping the smoke), the
  chain (solid, coloured by pack as in Figure 1) and the desk step (a lighter shade of the pack's colour); the time
  between segments left blank.

## 8. Tests that found defects before data was lost

- **Forcing problem.** A session of about five hours running new code on the real machine can fail in ways no unit
  test sees: a file rewritten without updating the stored hash that names its bytes, a schema mismatch only the live
  path builds, a launch route (§4). A failure found in a real session costs the session.
- **Claim.** Three kinds of live test, each with a written expected result and no override of any check, found the
  defects below before any run of the claim collections was collected on the faulty code: the machine test (three
  tries on 16-17 October: two failed, each for defects since fixed, then one passed), the smoke before each session,
  and the pre-check itself (§4). The one smoke hold of block 6 was judged wrong, and the smoke rule behind it (it
  read a repeated run's exit code 1 as a failure) was listed for repair, because under §5 only a measured physical
  hazard, or a condition under which no number of the registered experiment would exist, may stop collection.
- **Evidence.** `RUN_STATE.md:93` (first machine test failed: root cause), `:114-115` (second: three desk defects),
  `:122` (third passed); `docs/process_traces/2026-10-17-magistrate-d34bf254/RECORD.md:17-38` (the three desk defects
  and their effect), `docs/process_traces/2026-10-17-magistrate-52d50d1f/RECORD.md:10-18` (the passing test's
  injected faults and their records); `RUN_STATE.md:159-163` (the smoke hold);
  `docs/process_traces/2026-10-17-magistrate-57e84ae6/RECORD.md:7-14` (a smoke false alarm); registration `:425-431`
  (each pack's first session examined for structure before the next arms).
- **Status.** Writable now.
- **Worked example (real, structure).**
  - *Machine test 1 (16 October).* All 4 runs died about 0.5 s after starting: the smoke's preparation rewrote the
    plan file but left the file holding its SHA-256 digest naming the old bytes, so the integrity check rejected
    every run. The loop's own smoke used the same code, so round 1 could never have armed. The same test found that
    the driver built the agent-presence flag without one required clock field (`monotonic_raw_ns`), so the flag was
    rejected and only logged. That flag records a run that overlapped an agent, and the registration excludes such a
    run; with the flag rejected, round 1 could have counted it (`RUN_STATE.md:93`).
  - *Machine test 2 (17 October): three defects in the desk programs.* (1) The shared *admission check* (the test
    each run's idle baseline must pass before its measured request may start) still applied block 5's busy-fraction
    veto (it rejected an idle baseline whose CPU was often busy even when its power was low), which block 6's rules
    had made a flag. Two runs that had succeeded were excluded. In round 1 this would have silently dropped every
    such run and reference run, changing which references survive and so the allowed difference the drift screen
    judges against. (2) The test deliberately kept one run's idle baseline busy until the run was skipped at the
    *cap* (the longest a run may wait for a quiet idle baseline, 1,500 s). The structure check read any run with
    missing files as a stage that had left no records, so it called that skipped run a missing stage, ground S of §5,
    which would have removed the whole session. (3) The smoke's *classifier* (the program that marks each smoke stage
    passed or failed) failed any stage with a nonzero exit code; a skipped run makes its stage exit with code 1, so a
    chance skip in a real smoke would have held the loop. All three were fixed before round 1 (in one reviewed code
    change, pull request #501; `RUN_STATE.md:115`;
    `docs/process_traces/2026-10-17-magistrate-d34bf254/RECORD.md:27-38`).
  - *Machine test 3 (17 October, passed).* An injected agent process (alive 15:40:39 to 15:41:25) paused the chain
    for 630 s and the overlapping run was excluded by the agent flag; an injected busy load kept one run's idle
    baseline from passing, and the run was skipped after 18 admission attempts over 1,360 s, under the 1,500 s cap,
    and flagged `idle.wait_cap_skip`, as registered.
  - *The smoke hold (19 October).* ALPHA's round-2 smoke had one run that exited cleanly but whose clock anchor (§3:
    the placement of its records on wall time, from its own clock readings) could not be computed (the runner's own
    words: "anchor fallback rerun required"), so the run had to be repeated, which full sessions already handle: the
    same event appeared in r1-alpha in 2 stages, r1-beta in 1 and r2-beta in 3, and in each of those sessions the
    affected run was repeated, every planned run ended present and succeeded, and the session counted
    (`RUN_STATE.md:160-161`). The smoke rule read the stage's exit code 1 as a failure and held the pack (stopped
    arming it until the orchestrator looked). The orchestrator, woken by the loop, judged the hold wrong and resumed
    the pack within the 11 minutes it ran after the loop woke it; the loop had already moved to the next pack.
- **Figures.** *Figure 13: what each test catches.* A matrix: rows are defect classes found in October (stale plan
  digest, flag schema, busy-fraction veto, a run skipped at the wait cap read as a missing stage, smoke exit code,
  launch route, media daemon), columns are "unit tests", "machine test", "smoke", "pre-check", "full session"; a
  filled cell means "this test caught it", an open cell "it would have", a dash "it cannot". A legend names the three
  cell marks.

## 9. Blinding, the blind dry run and the independent recompute

- **Forcing problem.** Block 6 estimates the same quantities as block 5. If either block's numbers were read before
  every rule and program was fixed, any later choice could lean toward a preferred result, and a reader could not
  tell. And one analysis program can carry one defect into every number.
- **Claim.** Every block-6 decision that could change a printed number was made while block 5 was still blinded, and
  block 6 stays blinded until its collection has ended, block 5 has been released, the analysis programs have run end
  to end over every real block-6 archive writing structure only (the *blind dry run*) without any program stopping
  with an error, and a second program sharing no code with them (the *independent recompute*) agrees with them within
  a registered tolerance: each run's phase energy within 1 mJ, and every printed quantity within half a unit of its
  last printed digit.
- **Evidence.** Registration `:267-282` (terms), `:1122-1166` (what is restricted, what may happen blind, the release
  conditions, the tolerance and its derivation); `RUN_STATE.md:64` (the blind decisions of 14 October).
- **Status.** Mechanism writable now. The observed agreement and the release record wait for the release.
- **Worked example (real, non-claim).** An independent program applying the overlap sum (§0 item 6) to the
  rehearsals' raw power records reproduced 154 of 154 phase energies within 7 × 10⁻¹⁵ J. The 1 mJ tolerance therefore
  sits far above rounding (a 1 ns edge rounding at 42 W is 4.2 × 10⁻⁸ J) and far below the defects it must catch:
  moving one phase edge by 1 ms changes a rehearsal prefill by 0.047 J, 47 times the tolerance, and dropping one
  power record changes it by 3.4 to 5.5 J.
- **Figures.** *Figure 14: the path from raw bytes to a printed number.* Two parallel columns from one box "raw power
  records and stamps (the session's preserved raw files)": left column "harvest → analysis programs → restricted
  results", right column "independent recompute (no shared code) → restricted results"; a diamond "agree within 1 mJ
  per phase and half a printed digit?" joins them; its "yes" exit leads to "release entry (digests of registration,
  flag catalog, harvests)" and then "printed number", and its "no" exit to "no release: find the cause, then compare
  again". A dashed box around everything above the release labelled "blinded: structure only leaves this box".

## 10. How the software was built and checked

- **Forcing problem.** The collection and analysis code was written mostly by AI coding agents. A builder's own green
  tests do not show that a number is right: in the block-6 build, the defects that changed which data count were
  found by live tests and by reviewers running the code, not by the builder's tests (records below).
- **Claim.** A review procedure in which a second AI model session, not the author, runs the code on inputs built in
  the shape and size of real session files (*production-shaped* inputs; an *executing review*), and, for code that
  touches measurement or the counting decision, two further reviewers of different model families, each starting with
  no part in the work (*cold*), do the same without seeing each other's report (*blind cold passes*), caught defects
  that each single reviewer missed. The paper reports this as engineering evidence with its catch record, not as a
  claim about AI.
- **Evidence.** `docs/process_traces/2026-10-17-magistrate-d34bf254/RECORD.md:72-75` (the machine test caught three
  number-touching desk defects; each blind cold pass caught one major defect the other missed);
  `docs/process_traces/2026-10-17-magistrate-1a1261a5/RECORD.md:14-17` (reviews of the first machine-test fixes: no
  wrong number or lost run found, both original defects confirmed fixed on the real paths);
  `docs/process_traces/2026-10-21-magistrate-283e9802/RECORD.md:21-24` (both cold passes found the same formula error
  in a written fix instruction drafted by the orchestrator); `docs/orchestration.md:76-137` (when reviews and cold
  sign-offs run, and what each protects); `docs/process_prune_2026-09-29.md` (the six conditions a merge must meet).
- **Status.** Writable now. Open question for Ed: whether this belongs in the paper or in a separate report.
- **Worked example (real).** The second machine-test fix: one blind pass (by the AI model Fable 5.1) found that the
  program that writes the verdicts (§0 item 22) still rejected runs whose idle baseline was often busy but drew
  little power (the busy-fraction veto of §8); the other (by the AI model Opus 5.5) found a defect in how a run
  skipped at the wait cap (§8) was treated. Both defects change which data count; neither reviewer found both.
- **Figures.** *Figure 15: the merge path of one change to code that computes or selects a number.* A left-to-right
  flow: "builder (one model session given the job) writes code and its tests" → "executing review by a non-author
  (runs the code on production-shaped data)" → two parallel boxes "blind cold pass, model A" and "blind cold pass,
  model B" → "each finding fixed, deferred to a named later piece of work, or rejected with a reason" → "whole test
  suite run on the code as it will be after the merge, and the project's automatic test service (CI) passing" →
  "merge; a change to code that sessions run is pinned again, by a dated addendum to the registration (§0 item 24)".
  Each arrow labelled with what is handed over (code, report, findings).

## 11. Results: the replication (waits for the release)

- **Forcing problem.** Block 5's statistical intervals (the uncertainty ranges printed with each cell) hold variation
  inside one afternoon only; they say nothing about another day, another reboot or another time of day.
- **Claim (to be filled at release).** Block 5 and block 6 printed side by side under block 5's unchanged arithmetic,
  with their difference per printed quantity; a between-session summary per quantity (each counting session's value,
  their mean and standard deviation, and no interval that pools the sessions' runs as if they were one session); a
  GAMMA contrast called *replicated* only if every counting block-6 session gives the same outcome word and the same
  sign of the estimate; the flagged-inclusive line (the sessions that do not count, added back where computable); the
  whole-machine line per phase with its boundary sentence; the battery-assist line; and the independent recompute's
  observed agreement.
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
    own, re-executed with the repository functions; registration `:899-1006`) show the arithmetic of each statistic
    the paper prints (a cell's mean and interval, a floor, a contrast and its outcome word).
- **Figures.** *Figure 16: one printed quantity across sessions.* For each reported cell (model × phase), a dot plot:
  x axis "session" (block 5's session, then block 6's three in collection order), y axis the cell's energy (J), each
  dot with its registered interval as a vertical bar and, as a lighter outer bar, its attribution floor (§0 item 27:
  the energy its phase edges can move, in joules); a horizontal line at the block-6 mean. *Figure 17: GAMMA's
  replication.* One panel per contrast (decode, prefill): x axis "GAMMA session" (block 5's, then r1-gamma, r2-gamma,
  r3-gamma), y axis "contrast, 8B minus 1.7B (J)"; for each session a dot at its estimate with its interval as a
  vertical bar, the dot coloured by its outcome word (a legend names the four words), and that session's own floor
  gate drawn as a shaded band around zero. Both figures are drawn blank (axes and legends only) until the release.

## 12. Limitations

- **Forcing problem.** A reader who builds energy benchmarks will look first for what the instrument cannot see.
- **Claim.** Each limit below is stated with its size where it has one; none is hidden in a footnote.
- **Status.** Writable now.
- **Worked example (real, non-claim).** The rails-to-machine limit in numbers: on session H the rails were 0.377 to
  0.379 of the whole machine for a 122B model and 0.330 to 0.352 for a 70B model (§2), so no single factor turns a
  rail number into a machine number.
- **Figures.** None.
- **Evidence and the limits, one paragraph each in the paper:**

- One machine, one OS build, one week of sessions (17-21 October): the replication is across days, not months or
  machines (registration `:86-95`).
- The rails are three on-chip sensors; power elsewhere is seen only at the meter, and the rails-to-machine ratio is
  workload-dependent (§2, worked example 2).
- The meter's boundary is DC input at the adapter's USB-C socket; the adapter's AC-to-DC loss is outside every
  number, and the cable's loss between meter and laptop is inside the machine number (registration `:1035`).
- The battery current is read once a second, so block 6 gives the battery term per request, not per phase; and its
  energy is recorded up to 2.302 s after it flows (§6), so where it is split by phase (BYTES) it can fall on the
  wrong side of an edge.
- The capture's pulse-derived timing bound is measured on GPU pulses; applying it to sustained mixed inference is an
  assumption that M13 checks only at the pulse transitions it timed (`docs/paper/draft-v2-skeleton.md:159`).
- The rules' cut-offs come partly from rehearsals during which an agent process was alive, drawing 0.02 to 0.03
  CPU-s/s; the quiet-machine kit's measurements replaced those cut-offs wherever the kit measured the same quantity
  (registration `:886-890`).
- The media daemon was held with SIGSTOP by hand; a reboot clears the hold (`RUN_STATE.md:134`).
- The conversion w = 5.432 J per CPU-second is the cost of a performance core (one of the chip's fast, high-power
  cores) at interactive priority; the quiet machine's daemons run at background priority on efficiency cores (its
  slower, low-power cores) (registration `:784-786`).

## 13. Availability and replication

- **Forcing problem.** A reader who wants to repeat the measurement needs every fixed thing named: which code, which
  models and runtime, which rules, which raw bytes. Without that list nobody else can rebuild the paper's numbers.
- **Claim.** A reader can rebuild the measurement from the repository: the registration, the pinned commit, the flag
  catalog, the hashes recorded for the model files and the versions recorded for the runtime, and the loop's
  configuration, plus the raw archives on request.
- **Evidence.** Registration `:506-547` (the pinned commit, the measurement checkout, code identity, and, at
  `:536-539`, the four files that compute each run's energy and its bounds, byte-identical to block 5's: the program
  that computes phase energies by the overlap sum of §0 item 6, the clock anchor, the capture estimator and the
  sampler reader); `docs/paper/draft-v2-skeleton.md:952-1525` (Appendix A, already written for the calibration
  method).
- **Status.** Writable now; the paths and digests of the released files are added at the release.
- **Worked example.** Storage, which decides whether raw archives can be shared: a session's bytes are mostly sampler
  text that compresses about 70 times (83.0 MB to 1.2 MB at zstd level 3, round trip byte-identical, on a non-claim
  rehearsal file; `RUN_STATE.md:64`); a collected session keeps about 43 GiB before compression (the folder holding
  every run's raw files, plus the harvest's archive; `RUN_STATE.md:38`).
- **Figures.** None.

---

## Relation to the existing drafts

`docs/paper/draft-v2-skeleton.md` is a methods paper on the calibration and the timing sensitivity of phase-energy
assignment, demonstrated on synthetic and historical data. This outline reuses its §2 and Appendix A.3 for §3 above
and adds the instrument chain, the hazard measurements, the rule set, the automation and the replication.
`docs/paper/draft-v1.md` is the earlier draft; draft-v2 is the one selected on 2026-09-05 (its header, `:1`).

## Open decisions for Ed

1. Title (front matter).
2. Whether §10 (how the software was built and checked) belongs in this paper or in a separate report.
3. Whether the paper prints session H's 70B and 122B examples (non-claim) or only the quiet-machine kit's.
4. The venue; its deadline sets whether the replication's release must happen before the first full draft.
5. The derivation of the factor one quarter in F_min / 4 (§5): the registration states the cut-off but records no
   reason for the factor, and the paper must give one. What is recorded is that no registered decision changes for a
   cut-off anywhere from 0.18 to 0.65 J, so the derivation can be one sentence and changes no number.
6. A photograph of the meter in place, for Figure 2. The tracked record says only that the meter is "inline on the
   charger path" (the adapter and its cable); the order adapter, meter, USB-C-to-MagSafe cable, laptop comes from the
   session notes and from Ed's own words ("the magsafe power supply", BAT-1 record `:4`), and needs his confirmation
   at the machine.

## Check run before delivery

- Every J and W value in this file was compared against its source: the quiet-machine kit of 16-17 October (M4's
  5.432 J per CPU-second and its background-priority 0.0862 J per CPU-second, M10's fit, M14's load steps); the
  rehearsals of 6 and 9 October (F_min 1.9 J from 45.7 ms × 0.041 J per ms, and its quarter 0.475 J, the 0.73 to 2.6
  J range of F_min over which no registered decision changes and its quarters 0.18 to 0.65 J, the 0.62 s prefill and
  the 4.96 J agent example, the 0.77 W and 0.24 W graphics cut-offs for the 0.62 s prefill and the 1.99 s decode, the
  0.2 mW and 1.3 mW of quiet GPU-plus-ANE power, the −0.09 ± 0.09 J per CPU-second regression, the 11.11, 11.44 and
  11.26 ± 0.38 J reference runs and the rule's predicted 104 and 107 J, the 0.47 J half-width, 0.047 J per ms, the
  26.1 J prefill and its quarter 6.5 J behind the 139 ms stop, 3.4 to 5.5 J per dropped record, 42 W and the clock
  rule's 0.21 J, 7 × 10⁻¹⁵ J, and the threshold note's sizes 0.19 J and 2.4 W); session H of 21 October (every value
  in §2 worked example 2 and in §6, recomputed from the session's harvest records and raw files with the repository's
  `km003c_parse` functions, including the 0.302 s largest gap between polls and the 14.7 W and 121.5 W readings at
  the request edges in §6's second and last bullets; except, in those two bullets, the 2.13 s longest stretch of late
  discharge readings and the −76 mA and −14 mA readings, from the BAT-2 ruling's own measurement, and the 0.78 to
  1.15 J of 122B battery energy recorded in decode, all by polls in its first 1.93 s, and the 92.0 W largest meter
  sample in decode, from BAT-1's recomputed table (§6 Evidence), which matches the BAT-2 ruling's own table to its
  printed digits; and BAT-1's 0.85 J and 5.0 to 6.4 J); the agent draw (8 to 47 W); the adapter (140 W); draft-v2's
  worked pulse from a July capture made before both claim collections (42.55 W pulse height, σ minimum 0.001 W); or a
  synthetic registration example (7.20 J and its parts; b_op 50.818 ms; the 2.36 J timing bound and its 40 W and 10 W
  records, 2.30 J and 0.06 J; the 0.5765 J floor). None comes from a block-5 or block-6 session. Block-5 and block-6
  values that appear are structure only: verdicts, run counts, one flag count (battery assist, zero), stage and
  session timing, and hazard readings (the block-5 drop in the adapter's output and the sleep after it, the block-6
  pre-checks before t0).
