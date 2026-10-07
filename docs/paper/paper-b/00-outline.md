# Paper B: outline, and where each result will go

<!--
Paper B outline and guide to the slot manifest (paper work-list item 2). Conventions for whoever edits this file:
1. It states no result of the three windows the paper reports, and hints at none. A place where such a result will
   be printed is written as a slot marker (Section 4), never as a number.
2. Every number taken from the registration, the analysis plan or the code is accounted for in a comment in its own
   paragraph: "rv:" gives its key in registered-values.json (this directory); "src:" gives the section and line(s) it
   was read from in configs/campaigns/v5_claim_25g83/registration_block5.md or analysis_plan_block5.md (revision 9,
   DRAFT, as they stand at commit 9b0c680ed); "calc:" shows arithmetic done here. After the seal every "src:" line is
   re-read against the sealed text.
3. The slot counts in Section 4 are checked against slots.json by tests/test_paper_b_slots.py.
4. A term is built in full in 01-terms.md. This file glosses a term in a few words where it first uses it and keeps
   the plain names of 01-terms.md; a repository label appears once, in parentheses.
5. The word "token" means a piece of text a model reads or writes, and nothing else. The written form of a slot is
   called a slot marker.
-->

This file is the plan of the paper: what it is about, which sections it has and what state each is in, and the
name and source of every value that will be printed once the measurements exist. It is not a draft of the paper.
None of the paper's own energy data has been collected yet, so no result appears below.

## 1. What the paper is about

Paper B is a capstone paper. It reports how much electrical energy the processor of one laptop spends while a
language model, running on that laptop, answers one input text, and how that energy divides between the two parts
of answering. The terms needed to read this plan are glossed here in the order they are needed; `01-terms.md` builds
each one in full, from the hardware up.

**The design is fixed before the data.** The *registration* is the document, written before any of the paper's
energy data exist, that fixes what is measured, in what order, with which limits, and which recorded conditions
take data out of a *claim* (a sentence of the paper that reports a measured result). A rule or a value is
*registered* when the registration states it. The *analysis plan* is its companion: it fixes every formula applied
to the collected data and what is printed. Both are drafts, at revision 9, and are about to be *sealed*: frozen by
an independent ruling, after which a rule changes only by a dated, reviewed amendment. This file was checked
against revision 9.
<!-- src: registration preamble l.3, l.10-13; analysis plan preamble l.3 -->

**What is measured.** The machine is one Apple laptop. The measuring programs ask its operating system, ten times
a second, for the average electrical power drawn by the processor chip (CPU, GPU and neural-network accelerator
together); each reading covers one short stretch of time. A reading is a *power record*, and the tool that produces
them is the *sampler*. A *request* is one input text (the *prompt*) handed to a model, and the output the model
generates in reply; models read and write text in *tokens*, pieces of text the size of a word or part of a word. A
request has two *phases*. In *prefill* the model reads the whole prompt and computes the first output token. In
*decode* it produces the remaining output tokens one at a time. The *phase energy* of a phase is the energy of the
power records that overlap it, each counted in proportion to its overlap. One run of one request in its own
process, with the recordings around it, is a *member*.
<!-- rv: member.sampler_rate_hz -->
<!-- src: registration §0.2 l.267-273; §0.3 l.277; §0.4 l.307-312 -->
<!-- calc: two phases are the two named -->

Two models are measured, the *1.7B model* and the *8B model* (Qwen3-1.7B and Qwen3-8B, each with its parameters
stored at 4 bits apiece). Each runs two *workloads*, a workload being a fixed prompt with a fixed output length. The
*decode workload* has a prompt of 42 tokens and an output of exactly 512 tokens; the paper reports its decode phase.
The *prefill workload* has a prompt of exactly 2,048 tokens; the paper reports its prefill phase.
<!-- rv: stack.quantization_bits --> <!-- rv: workload.decode.prompt_tokens --> <!-- rv: workload.decode.output_tokens -->
<!-- rv: workload.prefill.prompt_tokens -->
<!-- src: registration §0.5 l.323-331; §0.7 l.392-393 -->
<!-- calc: 1.7 and 8 are parts of the model names; two models, two workloads, counted from the cited lines -->

**Three windows.** A *window* is one unattended stretch of machine time in which a fixed list of members runs in a
fixed order. Inside a window, an *absolute repeat* is one member run on its own. A *quad* is four consecutive members
in the order A, B, B, A, where A and B are two conditions, the quad's two *sides*. The order is chosen against
*drift*, a slow change over a window in what the same work costs or in what the sampler reads: a drift that grows
steadily from member to member adds the same amount to the two A members as to the two B members, so it cancels
from the difference between the sides. A *null quad* has the same model and workload on both sides, so any
difference between its sides comes from the measuring instrument and the machine, not from what was run. A *unit*
is what the statistics treat as one independent draw: one absolute repeat, or one whole quad.
<!-- src: registration §0.7 l.410-411; §0.8 l.418-434 -->
<!-- calc: four members per quad, as the cited line states -->

The design has three windows.
<!-- src: registration §1 l.868 -->

1. The *1.7B window* (repository label: ALPHA) runs, for the 1.7B model and each workload, 10 absolute repeats and
   10 null quads.
2. The *8B window* (BETA) runs the same for the 8B model.
3. The *contrast window* (GAMMA) runs, for each workload, 10 quads with the 1.7B model on side A and the 8B model on
   side B, so that each quad sets the two models against each other.
<!-- src: registration §0.7 l.392-394; §0.8 l.427-429; §0.9 l.438-439; analysis plan §7.1 l.369-372 -->
<!-- calc: 1.7 and 8 are parts of the model names; list numbers 1, 2, 3 -->

Every window also runs *reference members*: runs of one unchanging job at the window's start, middle and end. If
those at the end read differently from those at the start, the machine drifted during the window; the *reference
drift check* tests that difference against a limit computed from reference members run before any other member.
Every window also takes a *timing calibration* before its members and another after them: a recording made while
the graphics processor is switched between work and rest at commanded instants. Comparing those instants with the
steps seen in the power records puts a limit on the timing error between the two.
<!-- src: registration §0.11 l.458-463; §0.12 l.489-495, 511-528 -->

**What can stop a window, and what can remove data from it.** A *physical hazard* is a condition of the machine
that would corrupt a measured energy if a window ran through it. Six are registered: the clock jumping or running
at the wrong rate, the machine off mains power or its battery charging, the operating system reporting thermal
pressure (that it is slowing the processor to shed heat), a competing process, too little free disk, and the
sampler not delivering records. A window is *refused* (it does not start, and the reason is recorded) for three
kinds of reason only: a hazard measured at that moment; an AI agent session running on
the machine (the project uses AI models as software agents between measurements, and one running during a window
would compete for the processor); or a machine whose operating-system build or model is not one for which the
limits for judging a timing calibration were derived.
<!-- rv: arm.hazard_modules -->
<!-- src: registration preamble l.32-34; §0.15 l.750-753, 758-760 -->
<!-- calc: six hazards and three kinds of reason, counted from the cited lines -->

Almost everything else that goes wrong is written down as a *flag*, one recorded fact, and a flag never stops
collection. (The few conditions that can still stop a window once it has started, such as a failed first
calibration, belong to the section on the measurement window.) The *flag catalog*, frozen together with the
registration, says for every kind of flag whether it removes the flagged member, removes the whole window, or is
only disclosed (reported with the results, removing nothing). A removed member takes its unit with it (one member of
a quad removes the quad), and the units that remain are the *kept units*.
<!-- src: registration §0.16 l.771-778; §5.1 l.1543-1549; analysis plan preamble l.26; §2.2 l.81-82 -->

A window is *claim-usable* when no window-removing flag fired and enough units are kept. In the 1.7B window and
the 8B window, every reported number must still rest on at least 8 of its 10 absolute repeats and at least 8 of its
10 null quads. In the contrast window, each of the two comparisons must still rest on at least 8 of its 10 quads,
and the reference member at the window's middle must have given a usable reading. An *attempt* is one try at
running one of the three windows. The *analysed window* of each is its first claim-usable attempt, and attempts are
never mixed: no member of one attempt is combined with members of another.
<!-- rv: catalog.cell_unit_minimum -->
<!-- src: registration preamble l.38-40; §0.7 l.409; §0.9 l.438-439; §0.16 l.788-793; §7.2 l.2791-2793 -->
<!-- calc: 10 planned repeats and quads, from the cited §0.9 lines; two comparisons, three windows; 1.7 and 8 are parts of the model names -->

**The four kinds of result.** Everything the paper will print from these windows is one of four kinds, each
computed by a registered formula.

1. A *reported cell* is, for one model and one phase, the phase energy averaged over the kept units of that model's
   own window, with an interval (the range the registered formula puts around that average, from the scatter of the
   kept units and the recorded timing limits) and an energy per token. Four are printed: decode and prefill for each
   model. Beside each one the paper prints the *attribution floor*, a separate estimate of how much phase energy
   could be assigned to the wrong phase because the edges of a phase are timed only to within the sampler's timing
   error. It is printed next to the cell and never added into the cell's interval.
2. A *detection floor* is, for one model and one phase, the largest difference the instrument and the machine
   produce when nothing differs; hence the smallest real difference the measurement can tell apart from none. It
   has an *absolute form*, from the absolute repeats, and a *comparative form*, from the null quads.
3. A *dominance ratio* compares two versions of one detection floor. Each energy has a *timing uncertainty*: the
   amount it could change if the edges of its phase moved within their timing limits. The ratio is the floor
   recomputed with every energy free to move within its timing uncertainty, divided by the same floor with every
   energy at its recorded value. A ratio of 2 or more means timing uncertainty at least doubles the floor. There are
   eight (two models, two phases, two forms), and four more, the *shared-sign ratios*, that recompute the
   comparative form with the shared part of the timing change pushing every kept quad in the same direction. Only
   if every ratio the analysis plan requires is 2 or more may the paper say that timing is what limits the floor.
4. A *contrast* is, for one phase, the mean over the contrast window's kept quads of the 8B model's side minus
   the 1.7B model's side. There are two, decode and prefill. Each is judged against the larger of the two models'
   detection floors for that phase, and ends in one of four registered outcomes: *not estimable* (an input the
   formula needs is missing or invalid); *not resolvable* (for instance, the estimate does not exceed the floor);
   *unresolved* (the interval around the estimate contains zero, or the test, corrected for there being two
   contrasts, does not reject); or *direction supported* (none of these; the direction is the sign of the
   estimate).
<!-- src: registration §0.9 l.438-443; §0.10 l.447-453; §1 l.872-875; analysis plan §4 l.203-204, 221-247; §5 l.284-287, 306-309, 330-333; §6 l.344-358; §7.1 l.369-377; §7.2 l.408-421 -->
<!-- calc: four cells = 2 models x 2 phases; eight ratios = 2 x 2 x 2; four more = 2 x 2; 1.7 and 8 are parts of the model names; list numbers 1 to 4 -->

Beside these the analysis plan registers *disclosures*: lines and tables printed with the results that change no
number, such as which units were removed and why, how many attempts each window took, and each reported cell
computed with and without the members during which the battery helped the mains adapter.
<!-- src: analysis plan §8.1 l.466-474, 483-496 -->

**How strong a sentence may be.** The *measurement boundary* is the set of components whose energy a reading
includes: here the processor chip, never the whole machine or the wall socket. The project's *claims ladder* fixes
how strong a claim may be. An *instrument result* says that, on this exact machine, software and measurement
boundary, a quantity was observed (repository label: L1). A *comparative result* says that one condition differed
from another, with intervals reported, the two conditions alternated in time, and the difference above the detection
floor (L2). Reported cells and detection floors are instrument results. The cells of the two models, printed side by
side, are still two instrument results, because the two models' windows ran one after the other. A contrast is a
comparative result only when every registered condition for one holds; otherwise its wording stays that of an
instrument result.
<!-- src: registration §0.19 l.859-863; §1 l.877-894; analysis plan §7.2 l.432-435 -->
<!-- calc: two models, two instrument results -->

**Blind until released.** From the first window's start until collection has closed, nothing computed from a
member's energy is shown to anyone. The *release event* is the recorded moment after which energies may be read; it
comes only after the whole analysis has been run once on the real files with its outputs hidden.
<!-- src: registration §8 l.2886-2897; analysis plan §3.2 l.186-195 -->

## 2. Sections of the paper

Each section has its own file in this directory, so that no two authors share a file. "Being written" means a
draft is in progress now, from the design alone. "Waits" means the section needs the results. "Not assigned" means
nobody has been given it yet; the file name is reserved here.

| File | Section | The question it answers | State |
|---|---|---|---|
| `01-terms.md` | Terms, built in order | What does each word of the paper mean, built from the hardware up? It is the authors' shared vocabulary; the paper's sections restate what they need. | being written |
| `02-introduction.md` | Introduction | Why measure the two phases separately, what is new here, and what does the paper claim and decline to claim? | not assigned |
| `03-window.md` | Methods: the measurement window | In what order does a window run its members, how long is each wait between them, and why? | being written |
| `04-hazards.md` | Methods: six hazards measured directly | What can stop a window before it starts, what quantity decides each case, and at what value? | being written |
| `05-flags.md`, `05a-flag-catalog-table.md` | Methods: flags, removals and the claim-usable rule | What takes a member or a window out of the results after collection, by rules fixed before any data? | being written |
| `06-reference-drift.md` | Methods: the reference drift check | Did the machine drift during a window, and what happens when a reference member's reading cannot be used? | being written |
| `07-battery.md` | Methods: battery evidence | What is recorded about the battery, and why is a battery that helps the adapter disclosed and not removed? | being written |
| `08-meter.md` | Methods: the whole-machine cross-check | How does the processor's energy compare with the energy entering the whole machine, measured by a second instrument? | being written |
| `09-analysis.md` | Methods: the four formulas and the order of analysis | How is each of the four kinds of result computed from the kept units, in what order, and from which files? | being written |
| `10-released-results.md` | Results already released | What do the earlier, finished measurement sessions on this machine establish (the limits against which every timing calibration is judged, and the choice of the prefill prompt length)? | held: what may be printed from those sessions is not settled |
| `11-results.md` | Results of the three windows | What were the reported cells, the detection floors, the dominance ratios and the two contrasts? | waits |
| `12-limitations.md` | Limitations and threats to validity | What does the design leave unmeasured, and what would overturn each claim? | being written |
| `13-discussion.md` | Discussion and conclusion | What do the results mean for someone measuring phase energy on this kind of machine? | waits |
| `14-related-work.md`, `14a-citation-verification.md` | Related work | What did earlier work measure, at what boundary, and with what timing resolution? | being written |
<!-- calc: six hazards, four formulas, three windows and two contrasts, as in Section 1 -->

The title and the abstract wait for the results. The title has a fixed part and a subtitle that is printed only
if every required dominance ratio is 2 or more. Section 4 names the value that decides this.
<!-- src: registration §1 l.874-875; analysis plan §6 l.357-358 -->

What each section must contain, beyond its question:

- **Introduction.** The limits of the claims belong here as much as the claims: one machine and one measurement
  boundary, one fixed decode prompt, one prefill prompt length, and phase energies assigned by overlap with power
  records, without a separate measured check of that assignment.
- **The measurement window.** The order of a window from its first calibration to its last, every wait and the
  measurement that sized it, what happens to a member that fails, what can stop a window after it has started, and
  how long a window takes. Figure: the window timeline.
- **Hazards.** For each of the six: why it corrupts an energy, the quantity measured, the registered limit, one
  worked case that passes and one that is refused. Figures: the path of a problem from hazard or flag to
  claim-usable, and the limit on the clock's rate drawn as a curve.
- **Flags, removals and the claim-usable rule.** What a flag records, the three consequences the catalog can
  assign, the 8-of-10 rule with a worked case, and the catalog itself as a generated table.
- **The reference drift check.** The reference members, the limit computed from them, the check, and the rule for
  a reference member whose reading cannot be used, with a worked case a reader can recompute. Figure: the reference
  members and the check on those that remain.
- **Battery evidence.** What is read from the battery and how often, the two registered reasons for disclosing a
  helping battery instead of removing its members, and what still removes a member (charging, loss of mains power).
- **The whole-machine cross-check.** Every element between the wall socket and the processor, what the second
  instrument does and does not see, and the registered statistics. It never enters a claim. Figure: the measurement
  boundary.
- **The four formulas and the order of analysis.** Each formula with a worked case on invented numbers that are
  labelled as invented, the fixed order of the analysis steps, and what the analysis never does.
- **Results of the three windows.** Tables and registered sentences in which every result is still an empty,
  labelled place (Sections 3 and 4), and nothing else. The data figures (cells with intervals, floors and their parts,
  contrasts against their floors) are drawn by code that is written and tested now on invented data and run on the
  real files after the release event.
- **Limitations.** Each limitation names its mechanism and what would overturn the affected claim, and presumes no
  outcome.
<!-- rv: catalog.cell_unit_minimum -->
<!-- src: registration §0.15 l.750-753; §0.16 l.777-778; §1 l.885-887; §9.2 l.3002-3010; analysis plan §8.2 l.608-611 -->
<!-- calc: six hazards; three consequences; 8 of 10 as in Section 1; two reasons are items 1 and 2 of the cited ruling; four formulas, three windows -->

## 3. Why results are slots

The paper's text has to be written before its results exist, and the analysis is blind until the release event.
That creates two ways to print something false. A writer can type a number from memory, or from a file that is not
the one the analysis wrote, and nothing in the sentence shows where the number came from. And a sentence written
before the data can lean toward an outcome, with a phrase such as "as expected", that the data may not give.

A *slot* removes both. It is a named empty place for one value. Its name is fixed now; its value does not exist
until the analysis writes it; and the only thing that can ever fill it is one named value inside one named file.
Results sentences are written around slots, so their wording cannot depend on what the values turn out to be.

## 4. The slot manifest

`slots.json`, in this directory, is the *manifest*: the list of every slot. Three words describe where a slot's
value will come from. An *artifact* is a file that the analysis or the harvest writes; the *harvest* is the program
run on a window's files after the window ends, which archives them, writes every flag, and decides whether the
window is claim-usable. A *schema identifier* is the version string that the writing program stamps into each
artifact of one kind. A *field* is a named value inside an artifact, written as a path: `cells[].mean_j` is the
value `mean_j` of one entry of the list `cells`.
<!-- src: registration §0.17 l.838-840 -->
<!-- calc: three words are artifact, schema identifier and field -->

Every slot records:

- its **id**, lower-case words joined by dots, with no digit;
- the **artifact** it is read from and the **field** in it, with a selector that picks the one entry meant (which
  cell, which contrast, which window);
- its **shape** and unit: a number, a count, true-or-false, a name from a closed list, a table whose number of
  rows is not known before collection, or one registered line of text with the numbers it carries;
- how its value is obtained: **copy** (the value is that field, copied or rounded conservatively) or **derive**
  (the value is computed from that field by a formula the analysis plan names, which the slot cites);
- its **basis**: *named* when the analysis plan itself names the field (or the kind of flag that is read),
  *inferred* when the plan names the quantity only in words and this manifest inferred the field from the code, to
  be confirmed once the plan is sealed;
- its **value**, which is null in every slot.

In paper text a slot is written as a *slot marker*: the id wrapped in braces, in the form the example below shows.
Before the release event a slot marker is all that may stand where a result will go.

**One slot traced end to end.** Take the average decode energy of the 1.7B model. Its id is
`reported.small.decode.mean`. The four parts say which group of slots it belongs to (its *family*, here
`reported`), which model (`small`), which phase (`decode`) and which value (`mean`). The manifest says it is read
from the artifact with schema identifier `joulewise.paper_reported_energy_projection.v1`, the file the analysis
writes for each reported cell; that its field is `cells[].mean_j`; that the cell meant is the one whose `cell_id` is
`d117-reported-mean-ph-decode-qwen3-1p7b`, an identifier fixed in the committed configuration of the 1.7B window;
that its unit is the joule; that its value is obtained by copy; and that the value is null. A results sentence then
reads:

> Decode on the 1.7B model took {{slot:reported.small.decode.mean}} J per request (interval
> {{slot:reported.small.decode.lower}} to {{slot:reported.small.decode.upper}} J), over
> {{slot:reported.small.decode.kept_repeats}} absolute repeats and {{slot:reported.small.decode.kept_quads}} null
> quads.

The test `tests/test_paper_b_slots.py` reads the code, without running it, and checks that the schema identifier is
the one the program `joulewise/paper_reported_energy.py` stamps, and that `mean_j` is a key that program writes into
a cell. Had the manifest said `mean_joules`, the test would fail. The same test fails if any slot has a value, if a
slot marker in this file contains a digit, or if a slot marker names an id the manifest lacks.
<!-- calc: 1.7 is part of the model name; four parts of the id; the cell_id and the schema identifier are identifiers, read from slots.json -->

**Where a value travels.** Every element of the diagram is named under it: five boxes, five arrows (a to e;
arrow e is the line that runs under the diagram from box 2 to box 4) and the mark R.

```
 [1 window attempt] --a--> [2 harvest] --b--> R --b--> [3 analysis] --c--> [4 slots.json] --d--> [5 section text]
                               |                                                ^
                               +-----------------------e------------------------+
```

- *1 window attempt*: the members of one window run and each leaves its *bundle*, a write-once directory of its raw
  power records, timestamps and summary.
- *a*: the bundles, and the logs, kept while the members ran, of the physical quantity behind each hazard (the
  battery's current, for example).
- *2 harvest*: one run per attempt. It writes the flags, the list of kept and removed units, the counts of what
  was collected, and the second instrument's file.
- *b*: the harvest's files for the three analysed windows.
- *R*, on arrow b: the release event. The harvest's files reach the analysis only after it, so nothing the
  analysis writes exists before it.
- *3 analysis*: runs once, in a registered order of steps, and writes the artifacts that hold the four kinds of
  result.
- *c*: one field of one analysis artifact, for each slot that holds an energy or something computed from one.
- *e*: one field of one harvest file, for each slot that holds only a count, how an attempt ended, or one of those
  logged physical quantities. Such values reveal no energy, so the blinding rule allows them to be read while
  collection is still going on; the registered step that prints them still runs with the rest of the analysis.
- *4 slots.json*: the manifest. It holds the name and source of every value and never a value.
- *d*: slot markers. The program that will replace each slot marker with its value does not exist yet.
- *5 section text*: the files of Section 2.
<!-- src: registration §0.3 l.303; §8 l.2886-2892; analysis plan §1 l.53-55; §3.1 l.159-172 -->
<!-- calc: element numbers 1 to 5, five boxes, five arrows; three analysed windows; four kinds of result -->

**The families of slots.** In an id, `<model>` is `small` (the 1.7B model) or `large` (the 8B model); `<phase>` is
`decode` or `prefill`; `<form>` is `absolute`, `comparative` or `shared_sign` (the four shared-sign ratios of
Section 1); and `<window>` is `alpha`, `beta` or `gamma`, the repository's labels for the 1.7B window, the 8B window
and the contrast window. "Read from" names the artifact in plain words; `slots.json` gives its schema identifier
and the program that writes it.
<!-- calc: 1.7 and 8 are parts of the model names; four shared-sign ratios, as in Section 1 -->

| Family | Ids | Slots | Read from | Printed in |
|---|---|---|---|---|
| Reported cells: average, interval ends, energy per token, members and units kept | `reported.<model>.<phase>.…` | 28 | the reported-cell artifact | Results |
| Attribution floor beside each cell | `attribution_floor.<model>.<phase>` | 4 | the reported-cell artifact | Results |
| Detection floors: the floor, its two forms, units kept | `floor.<model>.<phase>.…` | 20 | the detection-floor artifact | Results |
| Dominance ratios with numerator and denominator; whether every required ratio is 2 or more, and what the paper may then say | `dominance.<model>.<phase>.<form>.…`, `dominance.branch` and four more | 53 | the dominance artifact | Results; title; abstract; Discussion |
| Contrasts: estimate, its intervals, floor, p-values, outcome, strongest wording allowed | `contrast.<phase>.…` | 34 | the contrast artifact | Results; abstract; Discussion |
| Descriptive estimates beside each contrast: ratio of the two models' phase energies; difference per token | `ratio.<phase>.…`, `per_token_difference.<phase>.…` | 16 | the contrast artifact and the list of kept quads | Results |
| Disclosure: units removed from each cell and contrast | `kept.<model>.<phase>.removed`, `kept.contrast.<phase>.removed` | 6 | the harvest's list of kept and removed units | Results |
| Disclosure: every attempt of each window, with how it ended, why it was not claim-usable if it was not, its flag counts and the members it collected | `attempts.<window>.…` | 18 | the harvest's file for the attempt, its flag summary, and the count of members collected that is written when the window ends | Results |
| Disclosure: each cell and contrast without the members the battery helped | `assist.<model>.<phase>.without`, `assist.contrast.<phase>.without` | 6 | the flags | Results |
| Disclosure, proposed: each cell and contrast if removals for physical disturbances were not applied | `sensitivity.<model>.<phase>`, `sensitivity.contrast.<phase>` | 6 | the harvest's list of kept and removed units | Results, if adopted |
| Disclosure: whether the contrast window and each model's own window agree | `cross_window.<model>.<phase>` | 4 | the reported-cell artifact | Results |
| Disclosure: each contrast's interval against its floor; the effect of leaving out one quad | `decision_vs_floor.<phase>`, `leave_one_out.<phase>` | 4 | the contrast artifact | Results |
| Disclosure: what was recorded about each analysed window (the hazard measurements at its start, flag counts, battery, reference members) | `window.<window>.…` | 30 | the harvest's flag summary and the flags | Results; Limitations |
| Disclosure: the outcome of the deliberate clock step | `clock_step_control.result` | 1 | the flags | Results |
| Whole-machine cross-check, per window and model | `meter.<window>.<model>.…`, `meter.central_band.…` | 41 | the second instrument's file | Results |
| Design values printed with the results (prefill prompt length; models and software) | `identity.prefill_length`, `identity.stack` | 2 | the file that records the choice of prompt length; the recorded identities of the models and software | Methods |

That is 273 slots. The first six families are the results proper (cells, floors, ratios, contrasts and the
estimates printed beside them): 155 of the 273. The rest are disclosures and design values. The *deliberate clock
step* of the table is a control run once, after the members of the first window have finished: the clock is stepped
on purpose, to show that the clock's hazard measurement can see a step at all.
<!-- src: registration preamble l.41-42 -->
<!-- calc: 28 + 4 + 20 + 53 + 34 + 16 = 155; 155 + 6 + 18 + 6 + 6 + 4 + 4 + 30 + 1 + 41 + 2 = 273; reported: 4 cells x 7 fields = 28; "four more" is the 5 dominance slots not tied to one ratio, less the one named; first six families -->

**What is deliberately not a slot.**

- *Fixed sentences.* The analysis plan registers wording that is printed as written, whatever the results: for
  example that every cell was measured in one window, that the order within a quad was fixed and not randomized,
  and that a dominance ratio has no interval. `slots.json` lists 17 of them under `fixed_sentences`, each with the
  plan section that holds its text. Section authors copy the text from the plan; they do not rephrase it.
- *Registered lines with no source field yet.* Another 8 disclosure items are registered to be printed but have no
  field in today's code that a slot could name (for example the amount by which drift may have moved a window's
  energies, which the code reads through a function and not from one field). They are listed under `unbound_lines`
  with the reason. No slot marker may refer to them until the program that computes the disclosures exists and names
  its fields.
<!-- calc: 17 and 8 are the lengths of fixed_sentences and unbound_lines in slots.json -->

**Rules for section authors.**

1. A result of the three windows is never typed. It is written as a slot marker whose id is in `slots.json`.
2. No sentence states or leans toward a direction, a size or an outcome. Write the sentence so that it is true
   whichever value fills the slot.
3. A design value (a count, a limit, a duration fixed by the registration) is taken from `registered-values.json`
   in this directory and cited beside the number, as this file does.
4. A worked case uses invented numbers and says so in the same sentence.
5. If a sentence needs a value that has no slot, the slot is added to `slots.json` first, with its artifact and
   field; an id is never invented in the text, and the test fails on one.
6. The strongest wording a family may carry is recorded with it in `slots.json`: an instrument result for cells
   and floors; for a contrast, a comparative result only if the artifact's own field says so
   (slot `contrast.<phase>.ready`).
<!-- calc: three windows; list numbers 1 to 6 -->

## 5. What must exist before a slot can be filled

1. Three analysed windows: one claim-usable attempt each of the 1.7B window, the 8B window and the contrast
   window. The two contrasts, the dominance ratios and the detection-floor artifact need all three.
2. The release event (Section 1).
3. The analysis programs that are still to be written. At the code version this file was checked against, the
   artifacts' schema identifiers and fields exist, which is what the test checks, but several of the programs that
   will write those artifacts for these windows do not. Among them: the one that reads the list of kept units and
   applies it everywhere; the one that writes reported cells over kept units; detection floors and contrasts over
   kept units; the step that hands the floors and the contrasts the amount by which drift may have moved a
   window's energies; and the one that computes the descriptive estimates and the disclosures. `slots.json` names
   what each family waits on, by the label the analysis plan gives it in its list of open items (plan Section 13).
4. A ruling on where each value may be printed. The analysis plan lists a proposed place in the paper for most
   printed quantities (the descriptive estimates and the disclosures have none yet), and at present none is
   adopted: printing any result of these windows needs a ruling by a reviewer that took no part in the work.
   `slots.json` records each family's present state.
<!-- src: analysis plan §2.3 l.99-101; §9 l.615-617, 627-629; §11 l.656-669; §13 l.694-697; registration §1 l.896-897 -->
<!-- calc: list numbers 1 to 4; three windows; two contrasts; 1.7 and 8 are parts of the model names; Section 13 is the plan's section number -->

## 6. Open points

- **One document or two.** Whether these sections become a new paper or succeed the sections of the project's
  earlier methods paper (on how sensitive phase-energy assignment is to timing) is the project owner's decision.
  The text is needed either way, and the file layout above does not depend on it.
- **Sections not assigned:** the introduction, the results and the discussion (the last two wait for data in any
  case), and a section on evidence and code availability.
- **Held:** the section on results already released, until it is settled which numbers of the earlier sessions may
  be printed.
- **After the registration is sealed:** every "src:" line in this directory is re-read; the slots whose basis is
  *inferred* are confirmed or corrected; and the proposed disclosure in the table of Section 4 is kept or deleted
  according to whether it is adopted at the seal.
- **Terms this file uses that `01-terms.md` does not build yet:** kept unit, slot, slot marker, manifest, family (of
  slots), artifact, schema identifier, field, disclosure, timing uncertainty (of an energy), shared-sign ratio, and
  three of the four outcomes of a contrast (not estimable, unresolved, direction supported).
<!-- calc: three of four outcomes: the lexicon builds "not resolvable" -->
