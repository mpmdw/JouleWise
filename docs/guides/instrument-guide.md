# The JouleWise Instrument, Explained From Zero

*A guide for someone new to the project. It assumes you know what an LLM is
and roughly what "energy" means, and nothing else. It is deliberately more
thorough than the paper's methodology section: the paper argues; this
document teaches. Every mechanism is presented with the problem that forced
it into existence, because almost nothing in this instrument was designed
speculatively — nearly every gate exists because a specific failure
happened, or was demonstrated to be about to happen.*

*Status note: written 2026-08-18, on the Phase-2 transaction branch, the
morning the successor pack family reached its confirmation point.*

---

## 1. What this instrument is for

JouleWise measures the energy cost of large-language-model inference
operations — "how many joules does it cost this Mac to generate one token,"
"how much energy does processing a 256-token prompt take," "is the 7-billion-
parameter model's decode energy distinguishable from the 1.5-billion one's"
— on Apple Silicon, using only the machine's own telemetry.

The defining commitment is that every number ships with a demonstrated
error bound. Not an assumed bound, not a vendor specification, not a
statistical formula applied on faith: a bound the instrument itself
measured, on this machine, under the same conditions as the claim. The
project's one-line philosophy: **a measurement without a demonstrated error
bound is an anecdote.** Most published LLM-energy numbers on consumer
hardware are, by that standard, anecdotes — the related-work section of the
paper documents peer-reviewed studies that integrate the same telemetry
this project uses, with no calibration and no uncertainty treatment at all.

That commitment has an unusual consequence: the *primary product* of the
instrument is not the joule numbers. It is the **detection floor** — the
smallest energy difference the whole measurement system can honestly claim
to distinguish — plus the machinery that proves the floor is real. The
model-comparison numbers are then demonstrations of what a characterized
instrument can resolve.

## 2. The measurement primitive, and why it cannot be trusted blindly

Everything starts with `powermetrics`, Apple's built-in telemetry sampler.
Run with root privileges, it reports power draw for named "rails" of the
processor package — the CPU cluster, the GPU, and the ANE (Apple Neural
Engine) — as a series of samples, each an average over its sampling
interval. JouleWise integrates those three rails between operation
boundaries: energy = sum of (average power × interval duration), with the
boundary intervals clipped at the operation's start and stop events.

What Apple does **not** provide: a calibration certificate, timing
guarantees for when a sample's window actually began and ended, or
documentation of exactly which physical loads appear on which rail. Three
concrete consequences shaped the whole project:

- **Attribution is not guaranteed.** The sampler has its own clock and its
  own buffering; the workload has another clock. Nothing promises that
  "the sample stamped 12:00:00.100" aligns with "the token generated at
  12:00:00.100" to better than some unknown error.
- **Resolution is not stated.** Nothing says how small an energy
  difference is distinguishable from the sampler's own noise and the
  machine's background variation.
- **Rail coverage is not enumerated.** Some hardware is simply outside the
  measured rails. A small example the project verified directly: the
  keyboard backlight's LED power does not appear on the CPU, GPU, or ANE
  rails (established by code inspection of the power-management stack and
  supported by a documentation-grade probe that toggled the backlight
  between maximum and off under the sampler). The measurement boundary is
  therefore always named explicitly: *these three rails, nothing else* —
  not "the machine's power."

Because none of these properties comes from the vendor, the instrument's
job is to *measure its own measurement system*. Sections 4–6 are that
self-measurement; everything else is protecting it from contamination.

## 3. The two families of error

Every defense in this project targets one of two error families. Keeping
them separate is the single most clarifying idea in the methodology.

**Attribution error: the right energy, assigned to the wrong thing.**
If the clock alignment between workload and sampler is off by even a few
milliseconds, samples near an operation boundary get integrated into the
wrong operation. The total is right; the split is wrong. For whole-run
measurements this barely matters. For *phase-resolved* measurements — the
project's whole point — it dominates: a decode phase might last a few
seconds, and a misplaced boundary sample carries a meaningful fraction of
a small phase's energy.

The origin story that made attribution the obsession: an earlier
generation of the pipeline carried a **time-anchor defect** — the mapping
between the sampler's timestamps and the workload's timestamps was
subtly wrong — and when it was found, the project voided *every*
claim-eligible corpus collected under it and rebuilt the anchoring
machinery from scratch. That decision (repair, then re-collect, rather
than patch and excuse) set the tone for everything after: attribution
errors are silent, so the machinery that bounds them must be loud.

**Resolution error: a difference that isn't there, or a real one you
can't see.** Even with perfect attribution, the machine's background
activity, thermal state, and the sampler's quantization put a floor under
what can be distinguished. If two identical workloads, measured minutes
apart under the best possible conditions, differ by up to X joules, then
no claim of a difference smaller than X is honest — no matter what the
point estimates say.

Attribution is bounded by **calibration** (section 4). Resolution is
bounded by **floors** (section 6). The composed claim carries both.

## 4. The fiducial calibration: the instrument measuring itself

The calibration answers a concrete question: *if software commands a load
pulse at a known time, how far from the commanded edges can that pulse
appear in the sampled power trace?* The answer is a per-capture timing
bound called **b_fiducial** ("fiducial" as in a reference mark whose true
position is known).

**The protocol (version 3, frozen):** the workload drives 59 one-second
GPU pulses — each a 4096×4096 half-precision matrix multiplication loop on
the GPU — after 3 warmup pulses, with the sampler running at a 100 ms
cadence. The quiet gaps between pulses follow a deterministic
low-discrepancy schedule (deliberately irregular spacing) so the pulse
train cannot accidentally phase-lock with the sampler's own cadence. Every
capture records the raw sampler trace, the workload's event log, and a
clock anchor binding the two timelines.

**Detection:** an estimator searches the trace for the 59 pulses, jointly
fitting each pulse's start-edge and stop-edge displacement against the
commanded times. The accepted evidence is conservatively collapsed to one
symmetric worst-edge scalar per capture: the capture's b_fiducial is
driven by the *worst* pulse, not the average, because a phase boundary in
a real measurement gets no averaging — it lands where it lands. Across the
19-member corpus that grounds the current acceptance artifact, b_fiducial
ranges from 0.0227 s to 0.0336 s.

**Why pulses:** you cannot bound attribution error by measuring an unknown
workload — you need a signal whose ground truth you control. A commanded
square pulse is the simplest possible known signal: its true edges are in
the event log, its observed edges are in the trace, and the difference *is*
the attribution error, measured rather than assumed.

**The detection budget — and the night it proved itself.** The pulse
search is expensive, and a search that runs forever on a pathological
trace is itself a hazard. So the detector carries a preregistered
evaluation budget: if it cannot converge on all 59 pulses within a fixed
number of candidate evaluations, the capture is **refused as
non-convergent** — never accepted with a partial fit. On the night of
2026-08-17→18, the very first live capture under the current estimator hit
that budget and was refused. The diagnosis that followed is the best short
course on this project's method:

1. *Don't retry.* Rerunning until a capture passes is selection on the
   outcome — the cardinal sin. The refused capture's artifacts were
   preserved and studied instead.
2. *Discriminate instrument from environment.* Issued corpus captures —
   known-good traces — were replayed through the same detector. They hit
   the same budget. The previous detector generation, and the new one with
   a raised cap, both converged on all of them. Conclusion: the trace was
   fine (its pulse signal-to-noise matched the corpus); the budget had
   been set below the real workload's demand, a fact no repository test
   could expose because raw calibration traces are too large to live in
   the repository.
3. *Correct from the complete evidence, not until it passes.* Every
   retained raw trace on the machine — 34 of them — was swept; the maximum
   observed demand was 137,189 evaluations; the budget was reset to
   165,000, about 20% above the maximum, with the margin exceeding the
   entire observed spread.
4. *Then, and only then, re-derive.* The refused capture, re-evaluated
   under the corrected budget, converged on all 59 pulses and yielded
   b_fiducial = 0.0309 s — inside the issued corpus band.

A safety gate refusing on first contact with reality, the refusal
diagnosed rather than overridden, and the fix grounded in the full corpus:
that is the intended shape of every failure this instrument will ever have.

**Clock discipline.** The anchor between the two timelines is only valid
if neither clock moves during a capture. The system clock's network-time
synchronization can *slew* the clock mid-window — silently stretching or
compressing the timeline and moving energy between operations. So during
measurement windows, network time is disabled and re-enabled through two
narrowly authorized administrator commands (the only two privileged clock
operations the measurement account can run without a password; the
authorization was installed and exercised as part of operator
qualification). The anchoring machinery itself carries a 5 ms ceiling —
an anchor that cannot be established to better than 5 ms refuses the
capture.

**Bracketing and drift.** A single calibration is a snapshot. Real windows
are bracketed: a calibration before and after the science members, with
the timing allowance taken as the full disagreement between the brackets
(never less than a genesis lower bound of 10.818 ms, derived from the
historical range of 19 same-epoch bounds). If the brackets disagree by
more than 12.093 ms, the entire window is refused — that much drift means
the instrument was not the same instrument at both ends of the night.

## 5. The calibration acceptance: pinning the instrument's identity

A bound measured by one version of the estimator code says nothing about a
different version. So the instrument's identity is pinned cryptographically
by the **calibration acceptance artifact** — currently
`d079_calibration_acceptance_v2_n19_r2` — which records:

- the 19-member derivation corpus (every member's b_fiducial, byte-exact),
- the decision thresholds derived from that corpus,
- and the SHA-256 hashes of the four estimator source files that computed
  them (the fiducial estimator, the uncertainty machinery, the sampler
  adapter, and the reducer).

Any change to any of those four files — even a one-line comment — makes
every downstream consumer refuse with a *staleness* error, on purpose. A
changed estimator is a different instrument, and a different instrument
does not inherit the old instrument's evidence. When an estimator change
is genuinely wanted (the detection budget above was one), the acceptance
is **reissued**: the tool re-authenticates all 19 corpus members from
their raw artifacts under the new code, verifies that every scientific
value is byte-identical, produces a machine-checked delta report showing
*exactly one changed pin*, and only then may a new acceptance be issued.
The reissue is "science-neutral by construction": if anything beyond the
intended code pin differs, the tool stops. This happened twice on the
transaction that is now at its confirmation point — once for the audited
detection improvements, once more for the budget correction — and both
delta reports are custodied in the repository's process traces.

## 6. Floors: what the instrument may claim to distinguish

A **detection floor** is the empirically demonstrated smallest energy
difference the complete measurement system can distinguish for a given
operation family on this exact software stack. Not the sampler's noise
floor — the *system's* floor, including attribution error, drift, and
everything the protocol could not remove.

**How a floor is measured:** by running designed workload pairs whose true
difference is known — most importantly *identical* pairs, where the true
difference is exactly zero — and observing what the pipeline reports.
The observed spread of reported "differences" between identical workloads
is the false-difference scale; the floor is set above it.

**ABBA blocks.** The workhorse design: measure condition A, then B, then B,
then A. Any slow drift in the machine's state (thermal, background
services settling) affects the two A's and the two B's near-symmetrically
and cancels in the paired comparison. Simple alternation (ABAB) would
alias a linear drift straight into the A−B difference; ABBA cancels it to
first order. The floor packs use both absolute arms (single-condition
bundles, for level estimates) and ABBA comparison blocks (for difference
estimates): the current successor packs carry, per floor family, 10
absolute bundles plus 10 ABBA blocks of 4 members each — 100 science
configurations per floor pack, all frozen before any data is seen.

**The floors are attribution-limited, and labeled as such.** On this
instrument, the noise-limited component of the floor is around 0.3 J, but
the attribution term — b_fiducial applied at the phase boundaries —
dominates and lifts the working floor to roughly 1 J for the characterized
phases. That regime is a *ratified finding*, published as a label on every
floor rather than hidden: this project's floors say "attribution-limited,"
and a reader comparing instruments should understand that a better clock
anchor, not a quieter machine, is the upgrade path. Claims built on the
floors then carry additional pre-registered claim-side margins, putting
the effective bar for a claimed difference near 5 J. Numbers smaller than
the labeled bar are not claimed, full stop — the pipeline refuses to emit
them as findings.

**Per-phase, per-stack.** A floor is measured for a named operation family
(decode; prefill at a fixed 256-token prompt) on a named stack (exact
model artifact hash, runtime version, quantization, tokenizer, OS build).
Floors do not transfer across phases, prompt lengths, or stacks; the
256-token prefill floor is its own measured artifact precisely because
transporting a floor from a different prompt length would be an assumption
wearing a measurement's clothes.

## 7. The quiet machine: protecting the signal

Everything above assumes the machine's background is stationary and small.
It is not, unless forced to be. Resident daemons index files, analyze
photos, check for updates; the display and its friends draw power; other
software (including this project's own AI tooling) burns CPU. None of it
is distinguishable from workload energy after the fact.

The defenses, each with its scar tissue:

- **The screensaver story.** In an early floor campaign, 43 of 50
  calibration bundles were contaminated because a video screensaver
  engaged during the windows — the six "anomalously low" bundles were the
  *clean* ones. The protocol now forces the display asleep (a transient
  display-sleep command, not a screensaver), verifies screensaver
  disengagement, and treats display state as a first-class fence.
- **The process census.** Before quiet work, five process probes sweep the
  machine: a keep-awake census (no stray `caffeinate` holders), an
  agent census (no AI-tooling sessions), a browser census, a monitor
  census (no samplers or watchers already running), and a maintenance
  census (Spotlight indexing, photo analysis, software update, backups).
  The census patterns were themselves calibrated against reality: a
  qualification capture of the machine's true quiet state showed that
  several system daemons are permanently resident (seven Safari support
  agents with Safari closed; `watchdogd` matching a naive "watch"
  pattern), and the probe patterns are being corrected against that
  ground-truth fixture rather than against wishful assumptions.
- **Power and thermal fences.** AC power at full charge (a mid-window
  charge-termination is a step change in the power picture — this was
  observed directly during an operator qualification probe), thermal
  state nominal before starting, and at least ten minutes of untouched
  idle settling before any calibration.
- **The agent quiesce rule.** The project is developed largely by AI
  agents — and an agent session is background load like any other. No
  measurement starts while any agent session is active. The overnight
  first-light window was run by a single fenced driver script with every
  fleet shut down, and the driver's own censuses are part of the capture's
  custody record.

## 8. Frozen plans and the freeze ceremony

**Why freeze:** the most seductive way to corrupt a measurement campaign
is to adjust it after seeing data — drop the awkward bundle, tweak the
schedule, re-run the unlucky block. The defense is to make the plan
physically unchangeable before the first byte of data exists.

**What a pack is.** A campaign is compiled into a **pack**: a committed
directory containing every configuration the night will run (all 100
science configs for a floor pack), the order manifests fixing the
execution sequence, the calibration plan, condition-family definitions,
and a `plan_tree.json` that binds the pieces together with hashes. Packs
are generated by committed generator programs, so the entire pack is
reproducible byte-for-byte from its generator — and audited regressions
prove the generator cannot overwrite an earlier generation's committed
bytes (a defect class that was found, fought through seven rounds of
implementation and nine audits, and closed with generational proofs: the
version-2 packs can generate a version-3 family without touching version-1
or version-2 bytes).

**The freeze receipt.** Freezing a pack mints a receipt: a cryptographic
attestation binding the plan's exact bytes (via SHA-256 of the calibration
plan, which itself embeds the hashes of everything else) plus the
readiness evidence rows evaluated at freeze time. Two properties are
easy to miss and load-bearing:

- **The receipt *is* the frozen state.** The pack's descriptive text
  (README wording, status fields) is never rewritten after minting — an
  executed proof showed that any post-mint byte change to the pinned plan
  unconditionally invalidates the receipt at every later gate, with no
  re-mint path. So the committed receipt governs, and human-facing wording
  is written to be true both before and after freezing ("status governed
  by the freeze receipt") rather than flipped after the fact.
- **Receipts chain across generations.** A successor pack's receipt is
  numbered one past its predecessor's (`freeze-0002` chaining to the v1
  family's `freeze-0001`) and embeds an authenticated predecessor binding:
  the predecessor's pack digest, plan hash, receipt hash, and identity
  receipt, verified before the successor may mint. Superseded packs remain
  valid *historical* records — their receipts still authenticate — but the
  lineage is explicit and machine-checked in both directions.

**Identity-pin projection.** Before freezing, a projection tool reads the
*actual* model files and runtime the night will execute (the real
safetensors on disk, hashed; the real runtime identity) and pins them into
a projection receipt. This closes the gap between "the plan says model X"
and "the bytes on disk are model X."

**A subtlety that cost a night's receipts:** freeze receipts authenticate
the *absolute path* of the pack they froze. Receipts minted in a temporary
working directory are worthless on the real measurement night. The
project's receipts are therefore minted in the designated measurement
checkout — the exact directory the arm night will run from — and the first
set, minted in the wrong place, was reverted on the record and re-minted
correctly. (The revert commits are still in the history; honest history is
preferred over clean history throughout this project.)

## 9. Arming, the window, and the operator

A measurement night is a ceremony with a deliberately narrow shape.

**Readiness evidence with freshness horizons.** Before arming, evidence
rows are authored proving the machine and pack are ready — clock state,
quiet censuses, pack authentication, regression-suite results, and so on.
Volatile evidence (anything about the machine's live state) expires on a
20-minute monotonic horizon; procedural evidence lasts six hours. Expired
evidence refuses the arm. The horizons encode a simple truth: a statement
about a machine's state is only evidence while the state can't have
drifted.

**The single-use arm capability.** Arming mints a capability that the
launcher consumes *atomically, exactly once*. The launch either happens
under the armed plan or the capability burns — there is no
"launch, tweak, relaunch under the same arm." The consumption is bound to
the arm-time attested inputs through a five-hop digest chain, so a
substituted manifest or foreign context is refused before any filesystem
effect.

**The window chain.** The launched chain runs the pack's members in frozen
order, brackets them with the pre/post calibrations, writes runs into
custody-controlled roots, and refuses on any deviation — a boot change, a
clock event, an out-of-order stage.

**The trusted-operator boundary — stated, not hidden.** The instrument
does *not* defend against a deliberately dishonest operator, and the
threat model was explicitly ratified to exclude adversarial programs
running inside the measurement account. What the machinery guarantees is
that an *honest* operator cannot accidentally produce dishonest data: the
gates catch stale evidence, contaminated environments, plan deviations,
byte drift, and clock trouble. Fabrication by the single trusted human
with root access is out of scope — and the papers says so, because a
limitation stated is a boundary, while a limitation hidden is a landmine.

## 10. From samples to claims

The full pipeline, end to end:

1. **Plan** — packs generated, reviewed, committed.
2. **Freeze** — identity projected, evidence authored, receipts minted at
   the measurement checkout, everything pushed.
3. **Arm** — fresh readiness evidence within horizons; capability minted.
4. **Window** — quiet fences, clock discipline, bracket calibration,
   frozen-order members, bracket calibration, restore.
5. **Reduce** — for each member, integrate the three rails between the
   event-logged operation boundaries under the anchored clock; apply the
   bracket-derived timing allowance to every phase edge.
6. **Gate** — the whole-window verdict: acceptance artifact fresh and
   authenticated, brackets within drift allowance, pre-flight screen
   passed, custody complete, every member's lineage authenticated. Any
   failure refuses the window's evidence — recorded, not discarded.
7. **Claim** — only differences exceeding the labeled floor plus
   pre-registered margins, under the pre-registered statistical family
   (the first campaign's two contrasts form one Holm-corrected family at
   α = 0.05, two-sided, directions pre-registered), on the named stack,
   within the named boundary.

What a published claim finally says, in plain words: *on this exact
hardware, OS build, runtime, and model artifact, measured across these
three rails with attribution bounded by an in-window calibration, the
energy of operation A exceeded operation B by E joules, where E clears an
empirically demonstrated floor of F joules plus stated margins — and here
is the complete refusal log of everything the instrument declined to
claim along the way.*

## 11. The verification culture, briefly

Every mechanism above exists in code with fail-closed refusals, and the
project's process mirrors the instrument: implementations are audited
adversarially by independent reviewers, fixes are re-audited (fix rounds
have introduced defects often enough that the re-audit is mandatory),
consequential reversals go to cold reviews performed without the authors'
framing, and the operator is qualified through scripted evidence-producing
sessions. The project's own history is the argument: essentially every
failure class was caught by a *different* layer than the one that produced
it — the audits catch the implementations, the cold reviews catch the
audits, the operator's live runs catch what no sandbox could see, and the
instrument's own refusal gates caught a mis-set parameter on their first
night of contact with reality. The run reports under `docs/run_reports/`
are the evidence trail, and they are written to be read.

## 12. Glossary

- **ABBA block** — a measure-A, B, B, A schedule that cancels slow drift
  to first order in paired comparisons.
- **Acceptance artifact (D-079)** — the issued document pinning the
  calibration corpus, thresholds, and estimator code hashes; the
  instrument's identity card.
- **ANE** — Apple Neural Engine, one of the three measured rails.
- **Arm / arm capability** — the single-use, atomically consumed
  authorization to launch a frozen plan.
- **Attribution error** — energy assigned to the wrong operation because
  of clock misalignment between workload and sampler.
- **b_fiducial** — a capture's measured worst-edge timing bound: how far a
  commanded pulse edge can appear displaced in the trace.
- **Census** — the pre-window process sweeps proving the machine quiet.
- **Detection budget** — the preregistered cap on the pulse detector's
  search effort; exhaustion refuses the capture as non-convergent.
- **Detection floor** — the demonstrated smallest energy difference the
  complete system can distinguish for a named operation family and stack.
- **Fiducial pulse train** — the 59-pulse known workload used to measure
  attribution error.
- **Freeze receipt** — the cryptographic attestation that a pack's bytes
  are final; the receipt is the frozen state.
- **Identity-pin projection** — the receipt pinning the actual model and
  runtime bytes a night will execute.
- **Pack** — the committed, frozen directory of every configuration a
  measurement night will run.
- **powermetrics** — Apple's telemetry sampler; the measurement primitive.
- **Rail** — a named power channel (CPU, GPU, ANE); the measurement
  boundary is exactly these three.
- **Refusal** — a recorded decision not to admit evidence when a gate
  fails; the instrument's most common and most important output.
- **Window** — one uninterrupted, calibrated, quiet collection session.
