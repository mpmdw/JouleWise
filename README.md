# JouleWise


Terms used on this page: a *session* is one uninterrupted, unattended
collection of measurements on the dedicated laptop, a few hours long: an
opening calibration, a fixed list of model runs, then a closing calibration
(block 5's ALPHA session is 125 runs). A *run* is one execution of a model
on one prompt. The code and the sealed block 5 rules call a session a
"window"; [`docs/glossary_measurement_terms.md`](docs/glossary_measurement_terms.md)
defines each measurement term once and maps it to the code name that still
carries that word. A *pack* is the frozen campaign plan and its
authenticated supporting files; a *detection floor* is the largest false
difference the admitted measurement system can produce; a *mint* is the
governed process that issues a floor artifact; an *arm* is one pre-registered
workload or comparison track; a *verdict* is the final governed decision to
admit or refuse evidence; and a *refusal* is a recorded decision not to issue a
result when a required gate or piece of evidence fails.

**Now (2026-10-22):** the second collection of measurements meant to carry the paper's energy numbers is finished, and Ed has paused all measurement. Collections are called *blocks*: each is a planned set of sessions under rules written down in advance. After every session a desk program, run from a fixed, recorded version of the code, decides whether anything requires removing the session; it reads only which runs succeeded and what the machine's monitors recorded (for example, whether the clock jumped or another program competed for the processor), never an energy. A session it keeps *counts*. Block 5, the first block meant to carry the paper's energy numbers, has one counting session for each of three packs: ALPHA (the small model, Qwen3 1.7B, which has 1.7 billion weights, the stored numbers a model computes with), BETA (the larger model, Qwen3 8B) and GAMMA (the two models compared directly). One session shows how much a number moves from run to run on one day, not whether it holds on another day, so *block 6* repeats the same three packs with the same run lists and the same arithmetic, aiming for three more counting sessions of each. Its rules were registered (written down and frozen, after two independent AI reviewers checked them) on 17 October, before any block-6 data existed. Nine sessions ran from 17 to 21 October, three per pack; all nine counted, so block 6 closed at its target. Both blocks remain blinded: programs write their energies into files that no person or AI agent has read, so no choice about the analysis can be bent toward a result. On 22 October an audit of the stored data recomputed the fingerprint (a short code computed from every byte of a file, so that any changed byte changes it) of each of the 237,047 files that the twelve counting sessions use, three from block 5 and nine from block 6; every one matched the fingerprint recorded when the file was first stored. The same audit found that these files exist as one copy, on the laptop's single internal drive; where to keep a second copy is a question now with Ed.

On 21 October, after block 6 closed, the laptop ran a trial session for the next experiment, BYTES. BYTES asks whether the energy a model spends per generated token (a word or part of a word) follows the number of bytes the model must read from memory for that token; its draft plan covers ten models of 1.7 to 122 billion weights. The trial, item H in that plan, tests only whether runs finish and can be measured, how long they take and how hot the chip gets; none of its numbers will be reported as a result. Its 123 planned runs were five runs of each model (the *check runs*), twelve back-to-back repeats of each of two of the largest models (Llama 3.3 70B and Qwen3.5 122B), to see how hot the chip gets under sustained load, and 49 *reference runs*: fixed workloads, run mostly at the start of the session and again in the middle and at the end, which show how much the machine's readings of the same work vary and whether they changed during the session. Ed stopped it at 17:19 PDT, about five hours in, with 95 runs finished: all 50 check runs, 11 of the 12 Llama 3.3 70B repeats, and the 34 reference runs planned for the start and middle. The Qwen3.5 122B repeats and everything planned for the end of the session had not started. It showed four things.

First, BYTES includes a second copy of Qwen3 8B stored at 8 bits per weight instead of the 4 bits the other models use, so that one model can be compared at two byte counts: the 8-bit copy reads about twice as many bytes per token. It stays only if the energy of its generation phase (the part of a run in which the model writes its answer) can be picked out in the power readings and measured with a stated limit on its error; in all five of its check runs it could, so it stays. Second, for nine of the ten models a run took on average 1.5 to 2 times as long as the plan assumed (the 8-bit copy took a little less), because the plan's estimate left out loading and warming up the model, cooling down afterwards and processing the run's records. At the measured times one *pass* of BYTES (50 runs of every model, split over six sessions) needs about 33 hours of session time. Third, on 5 of the 16 finished Llama 3.3 70B check and repeat runs, the thermal-pressure signal of macOS (the operating system's own report that the machine is running hot) rose above normal. BYTES's draft rules, which reuse block 6's, leave such runs out of the main result (a second, labelled line of results puts them back in), so if that rate holds about one in three of that model's runs will be left out. Fourth, Ed asked whether the laptop ever draws more power than its charger supplies, so that the battery makes up the difference. In H it did, a few seconds at a time, on every finished check and repeat run of those two models; on Llama 3.3 70B nearly all of it came before the model began writing its answer, and the battery stayed fully charged throughout. The chip's own energy counters for its processor, graphics processor and neural engine (a unit built for machine-learning arithmetic), which carry the paper's main numbers, do not depend on where the power comes from. The whole-machine energy, read by a separate meter on the charger cable, misses the battery's share unless that share is added back from the laptop's battery-current sensor. Blocks 5 and 6 already add it back. BYTES's analysis code did not; on 21 October it was decided that it will, printing the battery's share as its own column. That change is written and is going through its independent reviews.

Next: finish block 5's analysis code (work item L9 in the project's records) and have two independent AI reviewers each run it; then add the block-6 parts, which set each block-6 session beside block 5's and summarise how much each number varies between sessions. Then the numbers are released (opened for reading), block 5's first: block 6 measures the same quantities, so reading it first would reveal block 5's numbers in all but name. Each release waits until the analysis code has run end to end over the real data while writing out no numbers, only whether each step worked, and until a separate program that shares no code with it has recomputed the numbers from the raw power readings and agreed within a margin fixed in advance. Ed wants a paper or two by mid-November: the first on the method and blocks 5 and 6, and a second on BYTES if its data are in by 1 November, otherwise BYTES becomes a section of the first. BYTES's draft rules therefore start no session after the end of 1 November (Pacific time), so its first pass, the minimum the plan requires, must fit before then. Before that pass, BYTES's list of models must be settled (on 22 October Ed asked for it to be checked against the strongest open models that fit in the laptop's 128 GB of memory; a survey of the candidates is done and its recommendation is with Ed), its rules registered, its session lengths set from H's timings (perhaps after a session of about four hours that finishes what H did not reach), and the battery change reviewed and adopted. Nothing is measured until Ed lifts the pause; the analysis and preparation work goes on meanwhile.

**Previously (2026-10-12):** the first measurements meant to carry the paper's energy numbers have been collected; the analysis comes next. The collection is called *block 5*. Its rules (what is measured, which checks remove a session, how the numbers will be analysed) were sealed by an independent reviewer before any data existed. It consists of three unattended sessions of about six hours, each a fixed list of model runs on the dedicated laptop: ALPHA (the small model, Qwen3 1.7B, 125 runs), BETA (the larger model, Qwen3 8B, 125 runs) and GAMMA (107 runs that compare the two models directly, in alternating order). A session counts only if a desk program, run afterwards from a pinned version of the code, finds no reason to remove it; that program reads counts and check results and never an energy, and nobody has looked at a measured energy yet, so no decision to repeat a session can depend on the result. All three now have a usable session: ALPHA (9 October), BETA (11 October, 122 of 125 runs succeeded) and GAMMA (the night of 11 October, at its first attempt, 103 of 107 runs succeeded). Getting here took eight removed or refused attempts, each kept and disclosed and never analysed. Their causes were found and cured one at a time: too few reference runs to check the machine for drift (the reference set was enlarged from 12 to 18 under a second seal); a laptop that went to sleep when the charger lost power for 26 seconds (a keep-awake job now runs permanently); an agent session opened at the keyboard during a session; and a registered rule under which one failed calibration capture removed every later session (corrected for later sessions only, by a reviewed amendment). The next work is the analysis code, written and reviewed before the measured energies are opened; opening them then needs an independent reviewer's approval.

**Previously (2026-10-02):** the timing calibration for the current macOS build (25G83) is issued: 24 calibration captures from two back-to-back sessions, judged by a cold independent reviewer before it became the live default. Every ordinary measurement had been refused since a macOS update on 2026-09-02 because the only calibration on file belonged to the old build. The next session is designed, its rules are sealed by an independent reviewer before any data exist, and the code it needs is merged: the *prefill probe*. The power instrument records one power reading every 100 ms, and the prompt-reading phase of a small model can be shorter than a few readings, too short to measure. The probe runs the small model (Qwen3 1.7B) five times at each of four prompt lengths (512, 1024, 2048 and 4096 tokens), with the larger model (Qwen3 8B) once each for the record, and counts how many readings overlap each prompt-reading phase. The shortest length at which all five small-model runs show at least five overlapping readings becomes the prompt length of the phase-energy paper's measurements. It computes no energy and makes no claim. The unattended scheduler arms it next.

**Previously (2026-09-26):** Ed made it binding on 2026-09-25 that the laptop battery must be full and not charging ("floating") during every measurement, because charging heats the chip and distorts energy readings. The first piece of the code that enforces this across every kind of session is now merged. It classifies each recorded battery reading as passing, charging-confounded or missing. If a record that should exist has been deleted, cut short or re-encoded, it refuses the whole computation rather than quietly dropping the affected capture. It also stops the idle-power experiment from being scheduled until its capture code records the battery state. Getting there took two independent rulings by a fresh reviewer, and the reviewer checking that ruling caught two cases where the first ruling would have wrongly treated an honest collector crash as lost evidence; both are fixed. A flaky timing test was also repaired. Next: the capture code and the result readers adopt the check, and the first calibration session runs once no interactive agent session is open on the machine. No measurement night is currently scheduled.

**Previously (2026-09-24):** the latest merged change strengthens the check at the planned start of an unattended measurement night: the dedicated copy of the code must still be clean and checkable after the check made when the night was scheduled, or the night refuses to run. A companion test proves that a night is refused if its table of measurement-night types gives the wrong capture length. The scored experiment is being built to compare how much measured energy two local models spend per correct answer on MATH competition problems at five difficulty levels. Its first active part is a *packer*, which assigns fixed groups of problems to capture batches (a *capture batch* is one continuous power recording and the problems run while it records) and, when an attempt runs too long, retries it in smaller captures so that every problem ends either measured or with a recorded reason why it was not. A separate checker was committed before the packer code; review found and fixed errors in both, and the packer now passes two stress runs of 300 planned problem schedules each. The most recent independent review then found a blocking defect: the packer's own self-check accepts a schedule that the separate checker rejects, so the two do not enforce the same rules, and a cached result lets a re-sealed schedule skip its replay. Packer coding is paused while two independent advisers propose a structural fix, which a fresh reviewer must approve before any more code is written. After that it still needs tests that vary every registered field and required rule, tests that deliberately break individual checks, and final independent reviews. The later steps that add up measured energy per problem group and compute the statistics wait for that reviewed schedule record and the analysis rules. A proposed analysis-plan amendment has passed its independent text review, but Ed must decide whether to adopt it, whether problem text may be published, how the models decode answers, the measurement budget and a check of the instrument’s minimum resolvable energy difference. The program that runs the scored measurement night is the next integration step. No measurement night is currently scheduled.

**Previously (2026-09-22, early morning):** the first idle-variance pilot night ran unattended end to end (armed 02:03, twelve 600 s idle captures 02:27–04:27, courier email 04:31, harvested and stood down 04:59 by the relaunched headless magistrate). The captures themselves were clean, but only two of twelve passed the timing check: macOS's time daemon nudges the wall clock by a few milliseconds at each network-time sync, and the check that maps the power sampler's timestamps onto the wall clock refuses any 10-minute capture whose clock moved more than 5 ms, a tolerance two orders of magnitude tighter than the ~1 J the instrument can actually resolve. That tolerance belongs to a reviewed method, so re-sizing it goes to a cold review before the pilot is repeated. Separately, the night's raw sampler files (130 MB each) exceed GitHub's file limit, so the results branch is unpublished until a destination is chosen; the bytes are archived locally with checksums.

**Previously (2026-09-22, overnight):** the unattended-night entry point now refuses to arm a new measurement night unless every earlier night still sitting in the custody directory has a terminal record (a completed delivery, a result file, a chain exit, or a refusal) and its scheduling span is over by the same rule the watchdog uses; a root that is still active, or that cannot be classified, stops the arm. The fix went through two cold-gate rulings after review found the explanatory text repeatedly drifting from the code; every rule sentence now has an executed probe behind it. The next real night is armed automatically once the machine is quiet (no interactive agent sessions open).

**Previously (2026-09-17):** the unattended-night hang of 2026-09-16 is cured and merged to main on 2026-09-17. Every custody-evidence read on the night path is now time-bounded and refuses with a named reason instead of waiting on a person; that refusal reaches the morning email; a night can only be armed after a probe run from a launchd job proves the same reads complete in budget; and the capture writer now re-reads the evidence corpus twice per slot instead of four times, so the arm-time probe's single measured pass certifies the writer fits. The wall-clock abort grace was settled by a cold-gate ruling and merged, and the pre-registration now carries the operational chain digest as its third revision. **The equivalence night is ARMED for 15:30 PDT on 2026-09-17** from a fresh clone at the merged main head; the launchd probe that gates the arm read the evidence corpus in under four seconds where the 09-16 night waited eleven hours. **Next:** the relaunched magistrate harvests after 18:05 PDT, applies the pre-written equivalence rule to the night's twelve captures, and takes exactly the one action that rule names.

**Previously (2026-09-16 early morning):** the scheduled-session installer and its follow-ups are merged, and the first rehearsal night ran end to end unattended (03:25 PDT: the chain fired, the courier emailed, the plan was harvested and retired by the relaunched headless magistrate). The next session is a real equivalence night, planned by the magistrate for a quiet machine. Two new reader-facing documents landed under `docs/process/`: the research prospectus (landscape, ranked questions, tool-release verdict) and the automation history (what it took to make sessions run without a human), both rewritten for a technical reader with no project background.

**Status:** The fallback methods/diagnostic paper is merged: it describes the measurement
honestly as energy assigned to inference phases from interval-average power records, with
its sensitivity to allowed timing changes, reports both historical model stacks, and keeps
everything that presumed the unperformed comparison in a separate prospective protocol
document. The retired dominance language is cleaned up repository-wide. The watchdog is live with a headless magistrate resident; the first post-watchdog rehearsal night ran unattended in the early hours of 2026-09-09 (result REHEARSAL_ONLY, chain exit 0) and surfaced one gate defect (the receipt tried to read a chain file the stub never writes), whose gate-side cure is now merged along with its arm/harvest record and the T38d checkpoint; two test-fixture lanes that made local full-suite replays flaky on this laptop (a sleeping sentinel fixture against a real capture deadline; live clock samples in the ARM integration fixtures) are also merged, and the last three full replays were completely green. Today's merged work: the paper now reports each per-model energy as a registered mean with a fixed-rule interval (D-179), carries a deterministic claim-side widening sidecar (D-178), and states the characterization omission and phase-attribution limitation plainly (D-177); the session-liveness census and its docs, the calibration-ledger custody probes with a backup-root override, and the D-176 pack-night go-receipt producer, consumer and rehearsal-control path are all merged, so the machine can refuse or admit a night without a person present. The three deterministic clock-refusal tests proposed by the fixture root-cause consult are merged too. On the evening of 2026-09-09 the unattended magistrate hit its usage limit and the laptop, unplugged, went to sleep, which stops everything; it is back on AC power with system sleep off, and the unattended loop resumes from where it stopped. Ed can now steer the unattended magistrate from his phone by opening a GitHub issue labelled directive, and the arm-recoverability rules he ratified on 2026-09-10 are recorded with their implementation lanes. The second stub night is armed for the early hours of 2026-09-11 (agents installed 04:10 on 09-10 by the unattended magistrate itself; the pre-night 07:00 dead-man firing stood down exactly as expected and its acceptance was ruled by a cold gate). On 2026-09-10 the resident magistrate audited every numeric acceptance gate between capture and a reported number (299 gates; Ed's ask: no barriers finer than the instrument): almost all are sensible and stay, the notorious 1e-15 turned out to be a decimal presentation quantum in an identity check rather than a measurement tolerance, and four real defects were found where a nanosecond of slack was compared against timestamps whose floating-point resolution is a quarter of a microsecond, so valid data could be refused by rounding luck; three are repaired with defect-shaped tests and merged this morning, one waits for the governed estimator re-freeze. The same sweep found that a fast probe member would not have supplied the 60 seconds of raw samples the clock-rate fit needs, so the diagnostic probe's idle capture grows from 30 to 75 seconds. A desk dry run then found that the macOS update of 2026-09-02 changed the machine under the timing instrument, so the issued calibration acceptance no longer describes it and no real session can run until a successor is derived. In the afternoon of 2026-09-10 the unattended magistrate built that machinery end to end and put it up for review: a derivation-only capture mode that licenses nothing, a second ledger session kind for capture nights, a validator that reads its limits from a per-generation registry row so the six existing artifacts keep validating byte for byte, a candidate issuer with a two-way proof of its statistics, an unattended night chain with a plan-pinned wrapper, and the rules written down before any data exists (three nights of twelve captures; no value examined before the third night closes). Every piece went through paired refuters, delta re-audits after each fix round, the magistrate's own reading of every production line, a fresh-eyes terminal review, and a clean full-suite replay at the exact merge candidate (every test passing, no waiver carried); the seat and refuter work ran on a single model family because the second family's quota was exhausted that morning, which is recorded as a limitation. That machinery is now merged to main. Late on 2026-09-10 the owner ruled on that plan: three blind nights are more machinery than this question needs, because the question is an instrument one — did the operating-system update move the timing bound or not? So the first night after the update is now a one-night equivalence check: a single quiet night of the same twelve captures, held afterwards against the timing envelope the calibration already in force carries from before the update. The rule for that comparison, the exact numbers it uses with the source of each, and the one action each of its three outcomes takes — inside the envelope, outside it, or too few usable captures to decide — were written down and merged before any data exists, along with the desk tool that applies them, which reads the night and reports a verdict and can issue nothing itself. If the night lands inside the old envelope, the calibration in force is carried onto the new operating-system build by a dated amendment that cites the night's own evidence, rather than being derived again; if it does not, the three pre-registered nights proceed and this night counts as the first. Next: harvest the stub night on the morning of 09-11; land the small mechanism that lets a passing night carry the calibration forward, which is in review now; then, if the gates pass, run the equivalence night in the early hours of 2026-09-12 from a fresh measurement clone, with the owner emailed before anything is armed. A passing night licenses nothing by itself: the first real diagnostic session follows the amendment, not the night. Detailed live state is in [`RUN_STATE.md`](RUN_STATE.md).
That file's generated state-kernel view owns current work selection.

## Current State

The phase framing in this section is historical; the live state is the `_v5` measurement campaign described under Status above. **Phase 2's Mac vertical slice is complete
and the project has proved its live measurement path on real hardware**
(2026-07-06). From a
typed config, one command produces a complete, schema-valid, auditable run
bundle and reduces it to energy/latency summary metrics — proven first on
deterministic mock adapters, and now live on real hardware: the MLX runtime +
`powermetrics` telemetry adapters measured Qwen2.5-1.5B-Instruct (4-bit) on an
Apple M3 Max. The energy values originally reported from that corpus are
**VOIDED permanently for claim use** because its power trace and workload
events were joined through the defective pre-repair time anchor (D-078).
They are not under re-adjudication and must not be quoted. The six real corpus
bundles pass `validate-bundle --strict`
read-only and unrewritten: strict re-derives the recorded powermetrics power
trace from raw plist evidence, re-derives summary metrics from the recorded
trace and event log, checks the legacy additive summary comparison, and
requires shape-valid provenance for new-era bundles. This validates the
recorded evidence path; it does not repair the physical time attribution or
make the voided energy values usable.

Unless a figure explicitly states otherwise, JouleWise uses gross measured
energy within the named measurement boundary as the headline basis. Gross
energy retains the idle, model-residency, and runtime overhead present during
the measured interval, so comparisons across devices, configurations, and
split versus monolithic execution use gross energy. Idle-subtracted energy is
reported separately as a within-device secondary view of activity above the
measured idle baseline; it is not used to rank devices or configurations. In
Q4, the fixed term is estimated from the gross-energy workload sweep and is
not set equal to measured idle energy. The advisor-review rationale and full
basis/boundary rule are recorded in
[`PROJECT_STATUS.md`](PROJECT_STATUS.md).

Under D-070, static batching, speculative decoding / native MTP, MoE versus
dense execution, quantization, and reasoning-length variance are five stress
tests of Q4's single thesis. The harness must instrument all five axes and all
five have strict-valid L0 smoke-bundle support plus characterization
commitments, but every study remains floor-gated, capped at L2, and sequenced
after the `_v5` campaign (the "Window A" sequencing this sentence used to name
was retired by D-167; "Window A" is the historical name of the July 2026
measurement campaign, a set of sessions and not a single one). See the fuller
[Q4 architectural stress-test agenda](PROJECT_STATUS.md).

D-075 now folds a ranked extension-axis evaluation into that same agenda
without proliferating theses: DSpark/DFlash break-even and control riders,
on-device quantized KV, one named hybrid pair, and attached
cache/context/kernel/backend provenance work. Every admitted unit remains a
floor-gated candidate at or below L2 with a named forbidden upgrade; unresolved
runtime and device-fit questions remain pending current external verification
(`NEEDS-WEB`), and Ed retains commitment
authority. Separate lead-run DSpark/DFlash smokes established native MLX
execution and per-round observability only. Their thinking-mode,
unmatched-output throughput inversion is hypothesis-generating, not energy
evidence.

Quiet-machine sessions still require Ed and a quiet Mac, and each one follows
the run-book: issue, or mint, the governed drift-bound artifact inside the session, then collect a start
triplet, midpoint reference, and end triplet around the science runs (the
runs whose energies are the result; the run-book calls a run a "member"). That
protocol ran five times and passed five times — the sessions named C, D and
a10, the 7B floor session, and the contrast session — under the merged screening and
uncertainty-budget rules (D-078 clause 10). One record-keeping caveat: for
a10 (and its reference session a9) the machine-readable verdict files were
not retained, so those "passed" results rest on the written close-out
record until a verdict is re-derived from the retained data. Those
pre-genesis results are
diagnostic or rule-establishing evidence, not the live claim path. Claim
authority arises only from the pre-registered `_v5` transaction nights
(decisions D-164 through D-167), after the shakedown night passes. The
alpha, beta, and gamma sessions under D-117, and the separately named
"Window C" characterization session (its historical name), were retired with the Qwen2.5 campaign
they belonged to (D-167); they are history, not a live path. The a8 retrospective path is closed, and the earlier
222-bundle floor publication is a permanently voided historical record under
D-078. Use the
generated state kernel—not this summary—to select the next live or agent-lane
step.

A separate nine-bundle follow-on remains as a historical, unmatched
instrument record. All nine bundles are strict-valid as stored evidence, but
their energy values are **VOIDED permanently for claim use** by the same
pre-repair time-anchor defect (D-078), not merely exploratory and not under
re-adjudication. Each model ran three repetitions of the fixed five-item
sentinel shape and emitted 1,280 generated output tokens per bundle.

| unmatched configuration | energy disposition | runtime-observed output throughput |
|---|---|---:|
| OLMoE-1B-7B BF16 | **VOIDED — time-anchor defect (D-078)** | 122.361 tok/s |
| Qwen3-4B INT4 | **VOIDED — time-anchor defect (D-078)** | 106.519 tok/s |
| Qwen3.5-122B-A10B INT4 | **VOIDED — time-anchor defect (D-078)** | 39.473 tok/s |

These points differ in model scale, architecture, tokenizer, and
quantization, so they do not establish a controlled scaling relation,
architecture effect, or efficiency comparison. The
[bundle-cited extraction](docs/legacy/process_traces/2026-07-17-exploratory-block/results.md)
preserves the original figures as historical evidence only; D-078 bars their
quotation or claim use.

Remaining backends plug into the same adapter interfaces: the fixture-first
2K NVIDIA stack (SSH transport, node worker, nvidia-smi + vLLM adapters)
includes NV-GATE-2 software hardening: per-backend raw-lineage verifier
registration, usage-first vLLM streaming, and identity-aware process-survival
handling. The NV-5 localhost lead gate passed 3/3, but ALL remote protocol
pins remain PROVISIONAL pending first live hardware contact; Jetson Orin (2L)
remains gated on device access.

The landed C-028 implementation and review cycle includes the frozen analysis manifest, the
production-uncertainty path, the campaign-verdict split, idle-dependence/HAC
uncertainty, the inter-token metric, doctor preflight, and the contrast/claim
engine. The analysis trio—manifest, verdict split, and contrast/claim
engine—is complete. The six frozen legacy arms, meaning the pre-registered
workload tracks, and 0.3.x/0.4.x dispatch rules
remain explicit; landed software is not being presented as new live evidence.
P0-003 closed with an iCloud Drive backup and a fresh restore that was
strict-valid and byte-identical. No new live NVIDIA or quiet-Mac measurement
is claimed here.

The post-audit landings add request-scoped AXI-SA burst/decode semantics,
freeze SPLIT-AP Part I before outcomes, close SITE-02's discovery and
emitted-code regression work, and establish AXI-SB's `supported` verdict from
lead-run B=2/B=4 Metal probes. The probes establish runtime feasibility and
request observability only; they add no energy result. The corresponding
AXI-SC pinned-runtime spike returned `unsupported_for_joulewise`: the external-
draft path lacks the full proposal/acceptance/decode-boundary observability
contract, and native MTP lacks a usable generation surface. No Mac energy leg
was minted from that negative applicability result.

The repository currently contains:

- Typed config and output schemas with JSON-Schema export and validation.
- Runtime, telemetry, and transport interface contracts, with shipped mock
  adapters and a backend registry.
- The runnable harness: bundle writer, controller lifecycle, reducer, a
  shared bundle read layer, static HTML report generator, and a CLI
  (`run`, `validate-bundle`, `reduce`, `report`).
- Example Mac-local and mock-local configs.
- Phase 1 methodology, feasibility, and measurement-design docs.
- A test suite run in CI on every push, including a mock end-to-end run and
  bundle validation. The canonical command below and CI output own the current
  result; reader docs intentionally do not copy its volatile count.

## Verify

```bash
python3 -m unittest discover -s tests
```

The command's output is the current result. CI runs the same suite; this page
does not pin a pass or skip count that would drift as coverage grows.

## Release

The ordered publication path, including private-corpus, network, Node/Lakebed,
and credential boundaries, is in
[`docs/publication_release_checklist.md`](docs/publication_release_checklist.md).
Its clean-clone fixture/component gate is
`python3 scripts/release_check.py --dry-run`; it performs real temporary-directory
builds and never deploys.

## Run The Harness (mock target — no hardware or extras needed)

```bash
# Produce a complete run bundle from the mock target (deterministic):
python3 -m joulewise run configs/examples/mock_local.json --runs-dir runs

# Structurally verify any bundle:
python3 -m joulewise validate-bundle runs/example-mock-local

# Re-derive summary metrics from a bundle's recorded trace/events (post-hoc):
python3 -m joulewise reduce runs/example-mock-local

# Render a static HTML run browser (first: pip install -e '.[analysis]'):
python3 -m joulewise report runs --output report
```

A run bundle (`runs/<run_id>/`) contains the normalized `config.json`,
`metadata.json`, the `events.jsonl` lifecycle/phase/token log, the raw
`power_trace.csv`, model outputs, per-component logs, and the reduced
`summary_metrics.json` (written last; its presence marks a complete bundle).

Bundles are immutable evidence: re-running the same config into the same
`--runs-dir` fails by design with a run-ID collision (D-010/D-022). To rerun
a member, move the old bundle aside, change `run_id`, or use a fresh runs
dir; collisions are refusals, not bugs.

## Config And Schema Verbs

```bash
python3 -m joulewise validate-config configs/examples/mock_local.json
python3 -m joulewise print-config-schema
python3 -m joulewise print-output-schema
```

## Documentation Map

**Advisor / high-level view:** `PROJECT_STATUS.md` is the standalone status,
plan, and architecture document - start there for a monitoring view of the
project.

See `AGENT_PLAN.md` for the phase index; each phase has a detailed plan and
an evidence-based exit checklist under `docs/phase_N/` — the exit checklist
is the per-item status authority (D-023). See `RUN_STATE.md` before starting
substantial work; its generated state-kernel region is the current
work-selection view. Mission M0 in `docs/agent_playbook.md` owns intake and
close-out; it routes the selected `docs/process/state_kernel.json` task to its
authority, acceptance criteria, plan, and phase checklist.

**Agents executing "the next step" start with `docs/agent_playbook.md`** —
self-contained, ordered mission guides (read-first lists, code-level routes,
verification commands, handoff checklists) for every remaining step of the
project.

Use the state kernel to add and rank new tasks; `TASK_QUEUE.md` is its generated
detailed projection plus dated history. Design decisions (with the options and
considerations behind them) live in `docs/decision_log.md`; risks,
triggers, and the descope ladder live in `docs/risk_register.md`; calendar
constraints live in `docs/milestones.md`; cross-model review sessions
(implementer/reviewer positions, votes, resolutions - see D-031) live in
`docs/council_log.md`. Under D-136, agents do not refresh, regenerate, or
deploy the status site. `docs/site/DRIFT.md` is a retained reference only; if
Ed chooses the manual workflow dispatch, Ed deploys the resulting snapshot.
