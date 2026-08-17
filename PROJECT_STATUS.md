# JouleWise: Project Status, Plan, And Architecture

Audience: project advisor. This is the standalone monitoring document - it
summarizes what the project is, how it is built, where it stands, and what
it needs, without requiring any other file. Pointers into the repository
are provided for anyone who wants the full evidence trail.

Terms used here: a *measurement window* is one uninterrupted, calibrated
collection session; a *pack* is the frozen campaign plan and its authenticated
supporting files; a *detection floor* is the largest false difference the
admitted measurement system can produce; a *mint* is the governed process that
issues a floor artifact; an *arm* is one pre-registered workload or comparison
track; a *verdict* is the final governed decision to admit or refuse evidence;
and a *refusal* is a recorded decision not to issue a result when a required
gate or piece of evidence fails.

- Freshness owner: phase completion lives in the phase exit checklists; live
  gates and work selection live only in the generated state-kernel regions of
  `RUN_STATE.md` and `TASK_QUEUE.md`; the canonical suite command and CI own
  the current verification result. This page deliberately does not duplicate
  volatile commit, pull-request, queue, or test-count facts.
- Repository state: `main` contains the repaired measurement instrument
  (D-078 phase 0), the audited screening and uncertainty-budget rules
  (D-078 clause 10; council C-045), and the first floor artifact minted
  on 2026-07-30. D-110 made that artifact non-claim-bearing. D-117 then
  retired the historical re-derivation/remint path.

  **2026-08-07 supersession (D-117): the historical a10/re-mint and old C/D
  plan are retired. Claim authority can now arise only from the prospective
  alpha, beta, and gamma windows; the separately named Window C
  characterization night remains Ed ruling #1.** The pre-genesis 7B
  calibration remains diagnostic evidence and design input for the fresh 7B
  floor window.

  The pre-registered head-to-head model comparison **collected and passed
  overnight on 2026-07-30→31** (40 paired measurements, with every
  collection-quality gate green). Its result remains a preliminary diagnostic,
  not a gated claim. D-117 requires the fresh prospective alpha/beta/gamma
  sequence before evidence can formally support a claim. As of 2026-07-30,
  the project's framing is **metrology-centric** (advisor-ratified): the
  measurement instrument itself is the product, and model comparisons
  demonstrate what it can resolve.

  The first two nights of the dedicated metrology campaign ran on 2026-07-31
  and 2026-08-01. The linearity data set is complete (40 of 40 runs). Two of
  the three planned "measure nothing and confirm the instrument reads zero"
  rungs are complete. The additivity data set stands at 23 of 24 runs from the
  second night's single collection root, with 21 of 24 corroborating runs from
  the first night. The measurements are collected, verified, and safely backed
  up.

  The automated end-of-night quality verdict for both nights nevertheless came
  back FAILED. The finding does not mean that the recorded data are bad. These
  were the first nights to end early under the campaign's safety rule that
  abandons a run after three environmental interruptions, and the verdict
  software had never evaluated that collection shape.

  Decisions D-100 and D-106 have now adjudicated the two nights. The first
  night's data cannot be promoted because its end-of-night calibration was
  recorded under a mismatched identity, an unfixable collection-time error. The
  second night's re-evaluation ran on 2026-08-03 after every required repair
  landed. The software correctly refused it because one measured run has a
  genuinely unresolvable internal clock alignment, and the fail-closed design
  will not certify a night containing it. A judge-style review confirmed that
  this refusal was the instrument working as designed, not a bug.

  **2026-08-05 supersession (D-113): Window B is permanently
  non-claim-bearing; its re-evaluation/license chain is retired and no
  set-aside or claim-consumption decision remains pending.** Those nights also
  produced two genuine instrument findings that will appear in the paper. The
  internal clock-alignment step operates with about a millisecond of margin —
  effectively a coin flip at the current capture length — and needs a small
  redesign. The operating computer's own text output can also spoil an
  admission check if it streams while a measurement waits for a quiet moment.
- Project phase: see the phase exit checklists for exact completion state;
  live eligibility and next work come from the generated state kernel, not
  this reader-facing summary.
- Repository: `github.com/mpmdw/JouleWise` (branch `main`)
- Live status site: https://quiet-signal-6af8833395.lakebed.app (Lakebed
  capsule; it is an Ed-deployed snapshot, not the repository authority.
  `docs/site/DRIFT.md` records known differences; agents refresh that report
  when front-facing state changes and never regenerate or deploy the site.)

## Current Repository View — 30-second read

**The repaired measurement path has produced its first floor artifact, but
that artifact is not currently claim-bearing.** The D-078 phase-0 repair
fixed the timing and calibration path on 2026-07-22; the drift-screen
rules merged on 2026-07-25; the first fully clean measurement windows
passed on 2026-07-25/26, and on 2026-07-30 the project minted its first
floor artifact from them. D-110 later made that mint non-claim-bearing,
and D-117 retired its historical re-derivation/remint path. Claim authority
can arise only from the prospective alpha, beta, and gamma windows; the
separately named Window C characterization night remains Ed ruling #1. A
second pre-genesis calibration window (the 7B model) passed overnight on
2026-07-29, surviving two
live contamination events that the admission gates caught and recovered
from per the written playbook. The earlier a5-a8 windows (229 members)
remain non-claim-bearing, instrument-proving evidence.

**The head-to-head comparison ran on 2026-07-30→31 and passed every
collection and whole-window gate.** Comparing the small (1.5B) and large (7B)
model decoding the same text, the large model used **about 147 J more energy
per response** on the whole-request, idle-subtracted diagnostic view. The
registered per-phase comparison metric gives **141.29 J**. The run-to-run
scatter of that difference across ten paired blocks was only about **0.24 J**,
roughly six hundred times smaller than the effect. This is the kind of
demonstration the metrology framing calls for: a real effect that the
instrument resolves with enormous margin under frozen, pre-registered rules.
This is a preliminary observation from the raw per-run summaries. The
comparison's bookkeeping schema landed on 2026-08-02, but D-117 requires a
fresh prospective contrast window before formal consumption. The same overnight session survived two
background-process intrusions — macOS's own malware scanner — which the
admission gates refused on the spot and the written recovery playbook
turned into a completed window with zero lost science measurements.

The earlier drift-screen problem is now resolved in the merged SCREEN+BUDGET
screening-and-uncertainty rules (D-078 clause 10). Gross and
idle-subtracted energy are screened separately; each passing window keeps a
nonzero drift allowance in its uncertainty budget; the drift bound expires
after 24 hours; fallback-clock members cannot support a floor; and mock
evidence is identified from the bound configuration and barred from claims.
This protocol has now run five times — windows C, D, a10, the 7B floor
window, and the contrast window — each minting its bound inside the
window and collecting three start references, one midpoint reference,
and three end references.
The older 222-bundle floor record below remains visible as a permanently
**VOIDED** historical record, not the current measurement posture.

AXI-SB remains `supported` for native static-batch runtime feasibility with
request-scoped observability; AXI-SC is
`unsupported_for_joulewise` on the pinned runtime because the required
speculative-decode/MTP observability or execution surface is absent. Neither
verdict is an energy result. Remote protocol pins remain PROVISIONAL, and the
generated state kernel remains the work-selection authority.

### Voided Window-A floor record

> **VOIDED PERMANENTLY FOR CLAIM USE (D-078):** the 2026-07-19 soundness
> audit found that the powermetrics trace timestamps and runtime events were
> joined through a defective time anchor. Every energy and floor value from
> this pre-repair corpus is void, must not be quoted, and is **not under
> re-adjudication**. The rows are retained only as a record of why the
> instrument repair was necessary. Record:
> `docs/reviews/2026-07-19-measurement-soundness-audit.md`.

| historical evidence group | disposition |
|---|---|
| request, phase, item, and suite absolute floors | **VOIDED — time-anchor defect (D-078)** |
| request, phase, item, and suite comparative floors | **VOIDED — time-anchor defect (D-078)** |
| start/end NEG-8 energy diagnostic | **VOIDED — time-anchor defect (D-078)** |

The original table and reference-pair values remain preserved in the immutable
evidence trail, but they carry no claim, comparison, or guard-floor meaning. Verified extraction:
`docs/process_traces/2026-07-17-floor-extraction/extraction-verified.json`;
reader deliverable: `docs/advisor_briefs/2026-07-17-window-a-brief.html`.

### 2026-07-19 re-calibration under the environment guard — VOIDED

The now-voided suite rows were re-measured in two bracketed windows under
the D-077 guard: **94 strict-valid bundles**, all admission predicates
satisfied. Its energy readout and provisional floor are **VOIDED permanently
for claim use** by the same pre-repair time-anchor defect (D-078), regardless
of their apparent repeatability. That corpus was also claim-ineligible on
source provenance (dirty collection tree); details:
`docs/advisor_briefs/2026-07-19-recalibration-update.html`.

UPDATE (2026-07-19 night): the clean re-run is done — 288 strict-valid
bundles with clean source provenance (`runs_recal3/4/5/6_20260719/`)
cover every planned Window-A cell except DF-TELEM at planned n,
including the complete n=10 suite-ABBA comparative cell; the source
provenance gate is closed. **SUPERSEDING UPDATE (2026-07-19/20): a
same-day soundness audit found a timing bug, and no energy number from
the existing recordings will be used for claims until re-measurement.**
In plain terms: the power meter and the workload log time on two
different clocks, and our alignment between them could be off by up to
~1 second. Energy is computed by summing meter samples inside the
workload's start/stop window, so a misaligned window integrates the
wrong slice of the recording — dramatic for short test runs and still a
meaningful hidden uncertainty on longer ones. Those numerical examples are
**VOIDED**, not corrected measurements. Nothing measured negative; the recordings are
intact and self-consistent; long-run repeatability (~0.3% across
nights) shows the platform is stable. Very short workloads are simply
below this instrument's resolution and will not be claimed — by
design, not workaround. The fix (align on the meter's own timestamps,
attach an explicit uncertainty range to every number, calibrate
end-to-end with 40 precisely-timed GPU bursts before new data) is
implemented and in adversarial review. Plain-language explainer:
`docs/advisor_briefs/2026-07-20-timing-defect-explainer.md`; technical
record: `docs/reviews/2026-07-19-measurement-soundness-audit.md`.

**REPAIR COMPLETE (2026-07-22): the instrument repair is finished and
signed off.** Over three days the timing defect was fixed and the whole
measurement chain was hardened through nine rounds of independent
adversarial review (each round tried to break the instrument; the last
round found one remaining gap, recorded below). In plain terms, the
instrument now: (a) knows precisely when its power readings happened
relative to the model's work (the clock-alignment fix, with the
alignment uncertainty — about 27 milliseconds — carried into every
result as an explicit error bar); (b) proves its own calibration is
genuine and fresh — a calibration recording that was tampered with,
mislabeled, taken under the wrong procedure, or older than 24 hours is
automatically rejected; and (c) refuses to report a result rather than
report a doubtful one, in every failure case we could construct. One
known limitation is recorded honestly: the file that stores the
detection-floor statistics is not yet cryptographically tied back to
the raw measurements it came from, so we only trust such files when our
own pipeline produced them in the same verified session (a fix is
queued). Live validation on the real hardware passed: the validation
recording (made under the earlier 40-pulse calibration procedure)
detected all 40 calibration pulses with no false detections, and a test
measurement reproduced the expected physics where the old defective
pipeline had been wrong by a factor of ~28. Production measurements
will use the newer 59-pulse calibration procedure, which supports the
stronger statistical guarantee we quote for the timing error bar.
Next: a fresh calibration and re-collection of the measurement campaign
under the repaired instrument. Record: `docs/run_reports/2026-07-20-p0-instrument-repair.md`.

**COLLECTION ERA UPDATE (2026-07-24): the repaired instrument has now
been proven in production.** Over two nights we collected 229 clean
measurements across four properly-bracketed windows. The standout
result: two identical reference measurements taken three hours apart
agreed to within 0.007 joules on a ~38.5 joule task — about 0.02%,
which is excellent repeatability for whole-system power measurement.
The windows are not yet "claim-grade" for one honest reason: our own
stability check (comparing a reference task at each window's start and
end) was found to be asking a mathematically unanswerable question, so
it failed every window on a technicality while the underlying data was
good. After a formal debate between the two AI models working on the
project — which the reviewing model won on one substantive point — the
check was redesigned and ratified: windows are now screened for
anomalous drift against a limit derived from measured repeatability
(instead of an arbitrary constant), and any drift observed is carried
into the results' error bars rather than being ignored once a window
"passes". Reference measurements are also being tripled at each window
edge. One collection session under the new rules produces the project's
first claim-grade detection-floor table, which then sizes the Splitwise
replication experiments. Records:
`docs/run_reports/2026-07-23-window-a-collection-arc.md`, decision log
D-078 clauses 8-10.

**SCREENING RULES BUILT, AUDITED, AND MERGED (2026-07-25; council
C-045).**
The redesigned stability screen described above is now implemented and
on main: both energy families are screened separately, every passing
window carries an explicit drift allowance into its error bars, drift
limits expire after 24 hours so stale calibrations cannot be reused,
and a measurement whose internal clock had to be guessed can never
anchor a result (that one rule alone corrected a floor that was
overstated by roughly a factor of three). The code went through an
unusually deep adversarial review — four independent audit rounds and
three rounds of cross-examination between two different AI models —
which caught and fixed several ways the new rules could have been
silently bypassed. The step-by-step measurement procedure for the next
collection session is written up in
`docs/phase_2/window_runbook.md`. Records:
`docs/run_reports/2026-07-24-screen-budget-gauntlet.md`, council log
C-045.

### Historical exploratory follow-on — energy values voided

Nine additional strict-valid, collection-usable bundles cover three
repetitions each of unmatched OLMoE-1B-7B BF16, Qwen3-4B INT4, and
Qwen3.5-122B-A10B INT4 configurations on the fixed five-item
`jw_mixed_v1_sentinel` shape. Every bundle is claim-evidence-flagged, the
model/config points differ in architecture, scale, tokenizer, and
quantization, and the repetition count is below the headline protocol. More
fundamentally, every energy value is **VOIDED permanently for claim use** by
the pre-repair time-anchor defect (D-078); this is not a pending
re-adjudication.

| unmatched configuration | energy disposition | runtime-observed output throughput |
|---|---|---:|
| OLMoE-1B-7B BF16 | **VOIDED — time-anchor defect (D-078)** | 122.361 tok/s (122.261–122.481 tok/s) |
| Qwen3-4B INT4 | **VOIDED — time-anchor defect (D-078)** | 106.519 tok/s (106.470–106.545 tok/s) |
| Qwen3.5-122B-A10B INT4 | **VOIDED — time-anchor defect (D-078)** | 39.473 tok/s (39.349–39.569 tok/s) |

Each bundle emitted 1,280 generated output tokens. The archived extraction
preserves the old energy fields, aggregates, and floor comparison as historical
evidence only; none may be quoted or used to support an efficiency or
architecture claim. Every raw repetition is bundle-cited in
`docs/process_traces/2026-07-17-exploratory-block/results.md`.

## Previous Update (as of 2026-07-09, C-027 whole-project council review) — 30-second read

**The project put itself in front of a hostile examiner and corrected
its own front page.** A seven-lens cross-model review (new Codex model,
extra-high reasoning) plus an independent final examiner audited the
docs, the scientific claims, the statistics implementation, the
architecture, and the operating loop itself. Verdict: the evidence
discipline and instrument core are sound, but reader-facing claims had
drifted from the evidence (the 1.5B per-token headline used the wrong
denominator; that correction remains part of the audit history, but the
underlying energy value is now **VOIDED under D-078**), the D-053
contrast-CI machinery exists as binding
specs but not yet as code (now owned as queue rows P2-037..P2-042 and
gating Window-A interpretation), and the loop's own audit trail and the
capstone-critical path (grading rubric, report skeleton, off-machine
backup, one data-to-figure slice) need attention before any new breadth.
All pre-repair energy values discussed in this historical update are
permanently void for claim use.
Full adjudicated record: `docs/reviews/2026-07-09-c027-whole-project-review.md`.

## Previous Update (as of 2026-07-09, advisor status cockpit) — 30-second read

**The public preview is being upgraded for live advisor observation.**
The project-status page remains generated from repository evidence, but
Lakebed now has a narrow fail-soft live overlay contract: freshness from
GitHub commit checks plus parsed current fields from `PROJECT_STATUS.md`,
`RUN_STATE.md`, `TASK_QUEUE.md`, and the risk register. The advisor
cockpit adds live snapshot state, attention items, campaign readiness,
evidence cards, and claim-ceiling panels; the Story page drops
hand-authored volatile counts. The operational policy is D-051: repo
markdown remains the source of truth and Lakebed never hides static
provenance. Current work follows `TASK_QUEUE.md`: C-019 shakedown, then
P2-015 quiet calibration for Window A (the CP-5 stop card was cleared
2026-07-09).

## Previous Update (as of 2026-07-08, all four streams merged) — 30-second read

**Everything landed.** The multi-stream session merged as four PRs:
P2-013 and P2-014 are closed — all 31 audit pins fixed, the suite passed
with zero expected failures (current count authority is RUN_STATE.md
Current Verification; the suite-build merge was 732 tests and the
post-alignment state is 734), bundle provenance
now records prompt/workload identities, and `validate-bundle --strict`
includes the powermetrics raw-plist-to-trace gate plus the legacy
additive-summary comparison. The six existing real corpus bundles pass
strict read-only and unrewritten; strict proves re-derivation of the
recorded evidence, not independent rerunning of the hardware session.
New-era bundles must carry shape-valid provenance to pass. The Stage
3.0.1 KV spike is merged with a lead-reverified verdict of
`replay_supported` (tokens identical; cache size +0.018% vs prediction)
— Phase 3's central technical risk is retired on current hardware. The
fixture-first 2K NVIDIA stack is merged; ALL its protocol pins remain
PROVISIONAL until first live hardware contact (the live-verification
checklist is ready). The independent project critique now carries a
second-pass reassessment (its recommendations that became code are
marked resolved; 16/17 of its checkable claims were lead-verified
against file evidence): `docs/project_critique_review.html`. Next: the
detection-floor calibration (P2-015) then the 2M two-model baseline
campaign on a quiet machine. Reader-facing status below defers to the
phase checklist matrix rows for per-item authority.

## Previous Update (2026-07-07, fifth update) — 30-second read

**The instrument grew four capabilities in one session and is now
campaign-ready.** *(Historical claim; C-027 (2026-07-09) supersedes the
gating: execution is conditioned on P0-003 backup, P2-038, P2-039, and
P2-015-SMOKE.)* Five parallel work streams landed (PRs #2-#6):
(1) **statistical uncertainty** — every multi-repetition experiment now
carries per-metric 95% confidence intervals with outlier detection and
explicit below-protocol flags, re-derivable byte-identically from the
raw evidence bundles (the live verification energy value is now **VOIDED
under D-078**); (2) **contamination detection** — an
idle-window quality gate that mechanically flags runs taken on a
non-quiet machine (it caught its first real contamination during
verification); (3) **deep telemetry** — per-sample GPU/CPU-cluster
frequency and residency forensics plus a machine-state snapshot in
every bundle; (4) **campaign automation** — a deterministic
config-matrix generator and a resumable sequential runner, so the
planned two-model baseline matrix (4 workload shapes × 2 models × 5
repetitions) runs unattended. A review council also produced a
hardware-tiered research agenda: 16 questions answerable on current
hardware alone, 10 more behind planned gates
(`docs/research_question_bank.md`). The P2-013 evidence-integrity and
P2-014 provenance fixes are now complete; next Mac corpus step is the
baseline matrix on a quiet machine.

## Previous Update (2026-07-07, fourth update) — 30-second read

**A flagship-class model was exercised through the live harness.** Qwen3.5-122B (Feb 2026
generation, 122B-parameter mixture-of-experts with 10B active, a
reasoning model) ran through the identical harness and workload on the M3
Max. The reported P2-003 and FLAGSHIP-001 energy values and their derived
cross-model interpretation are **VOIDED permanently for claim use** by the
pre-repair time-anchor defect (D-078); they are not under re-adjudication.
The runs remain evidence that both workloads traversed the live adapter and
bundle path. Also this update: the
research agenda grew to six named questions (Q4-Q6) after a
multi-model review council, with a curated question bank
(`docs/research_question_bank.md`) and an instrument roadmap (richer
telemetry parsing, a difficulty-graded scored workload suite, and
implementing the statistical-uncertainty protocol) queued.

## Update Ledger

| date | label | one-line outcome | run-report link |
|---|---|---|---|
| 2026-08-16 | Phase-1 repair code merged (five PRs); Phase-2 planned | The readiness council's entire mergeable Phase-1 program landed: the work-selection gate, the honest night-of-measurement capture contract, the claim-consumption edge (analysis accepts only authenticated finalized results), and the launch binding (arming and launching are one atomic authenticated step, hardened through an independent cold review). The Phase-2 re-freeze is fully planned with the operator-approval points mapped. | `docs/run_reports/2026-08-16-t9-session.md` |
| 2026-08-15 | Readiness council: NOT-READY 0/11; repair program adopted | An eleven-seat audit with adversarial verification ruled the instrument not ready to spend measurement nights; every finding became a work order in a four-phase repair program. The independent coverage re-audit later verified the calibration test universe end to end. | `docs/run_reports/2026-08-15-t8-session.md` |
| 2026-08-13 | All three measurement packs frozen | The alpha/beta/gamma campaign packs were frozen with passing receipts and the tighter pre-registered floor selector; the operator dress-rehearsal dry run passed all four hash-bound checks. | `docs/run_reports/2026-08-13-t6-session.md` |
| 2026-07-31 | Contrast window + D5-J merge (PR #89) | The 1.5B-vs-7B decode comparison window collected and passed every gate (47 bundles, ~147 J difference as a preliminary observation); the cooldown-evidence join redesign merged under a cold-gate ruling; the project's framing was adopted as metrology-centric — the instrument is the product. | `docs/run_reports/2026-07-31-contrast-window-collection.md` |
| 2026-07-30 | First floor artifact minted (PR #88; later tainted by D-110) | Mint #1 landed as a signed, validated artifact after a ten-round fix gauntlet and a cold-gate escalation ruling; D-110 later made it **NON-CLAIM-BEARING** pending governed re-derivation and remint. | `docs/run_reports/2026-07-30-mint-merge-coldgate.md` |
| 2026-07-29 | 7B floor window passed | The second calibration window (Qwen2.5 7B decode) passed its bracket and verdict, surviving two live contamination events; its floor mint is blocked by D-110's repair chain. | `docs/run_reports/2026-07-30-mint-merge-coldgate.md` |
| 2026-07-25 | SCREEN+BUDGET rules merged (PR #85) | D-078 clause 10 landed: separate gross and idle-subtracted screens, a nonzero drift allowance in every passing window's budget, a 24-hour bound expiry, and mock evidence barred from claims. | `docs/run_reports/2026-07-24-screen-budget-gauntlet.md` |
| 2026-07-22 | Instrument repair merged (PR #79) | The trace-time-anchor defect that voided claim use of the earlier corpora was repaired and confirmed end to end, reopening the path to claim-bearing measurement. | `docs/run_reports/2026-07-20-p0-instrument-repair.md` |
| 2026-07-19 | Measurement-soundness audit (Ed-directed) | VERDICT: unsound for claim-bearing use as recorded — trace-time-anchor defect misattributes request/phase energies (all four P0s lead-verified); metric-level prechecks already failed 238/288 request metrics; four cooldown cap hits unjoined; analysis-engine wire incompatibility. Pre-repair energies permanently **VOIDED** for claim use; instrument-repair path defined. | `docs/reviews/2026-07-19-measurement-soundness-audit.md` |
| 2026-07-19 | Extended clean-provenance re-collection | 266/266 strict-valid bundles with clean SOURCE provenance from clean main (288 total with the completion window); all planned cells except DF-TELEM executed at planned n; one unlock abort quarantined (guard's 4th live catch); Sol recompute audit PASS on arithmetic. See the superseding soundness-audit row above for claim status. | `docs/run_reports/2026-07-19-recal456-extended-window.md` |
| 2026-07-19 | Suite re-calibration under the guard | 94 strict-valid bundles; energy readout and provisional floor permanently **VOIDED** by the D-078 time-anchor defect; the corpus also failed the then-operative source-provenance gate. | `docs/run_reports/2026-07-19-d077-recal-window.md` |
| 2026-07-18 | Contamination diagnosis + environment-guard hardening (D-077) | Suite-cell inflation was attributed to the macOS video screensaver on an awake idle display (43/50 bundles; power-source hypothesis refuted); those pre-repair energies were later permanently **VOIDED** by D-078. The D-077 guard was built and taken through an eight-round adversarial arc. | `docs/run_reports/2026-07-17-environment-guard.md`; `docs/run_reports/2026-07-18-d077-fix-rounds.md` |
| 2026-07-17 | exploratory block + D-075 re-wrap | Nine retained OLMoE/Qwen bundles were re-validated and extracted as unmatched observations; their energy values are now permanently **VOIDED** by D-078. DSpark/DFlash smokes and D-075's ranked extension-axis intake folded in without promoting evidence. | `docs/run_reports/2026-07-17-window-a-floors.md` (final re-wrap addendum; lead gate pending) |
| 2026-07-17 | Window A floors + advisor brief | PRs #72/#74 closed the bounded powermetrics drain defects and P2-038 passed on merged main; PR #73 filed the AXI-SC negative verdict; 222 strict-valid bundles were extracted, but every reported energy and floor is now permanently **VOIDED** by D-078. | `docs/run_reports/2026-07-17-window-a-floors.md` (LEAD-ACCEPTED) |
| 2026-07-16 | audit close + no-hardware resumption batch | PR #66 closed the comprehensive audit; PRs #67-#70 landed AXI-SA, SITE-02 D1/D2, the SPLIT-AP Part I freeze, and the AXI-SB `supported` verdict with its Mac C5-2.2 leg. Window A is software-unblocked but still needs Ed + quiet Mac; no new energy measurement is claimed. | `docs/run_reports/2026-07-16-resumption-nohw-batch.md` |
| 2026-07-10/11 | C-028 hardening and integration arc | PRs #41-#58 merged; analysis trio complete; reducer lattice through 0.4.2; P0-003 restore proof and every Window-A software gate satisfied; PR #59 open as a bounded follow-up; no new live evidence claimed. | `docs/run_reports/2026-07-11-c028-continuation.md` |
| 2026-07-06 | third update / first live hardware path | Mac slices 2G/2H/2I landed and produced strict-valid M3 Max bundles, proving the live adapter and evidence path. Every energy value originally reported from this pre-repair corpus is permanently **VOIDED** by D-078 and not under re-adjudication. | `docs/run_reports/2026-07-06-slice-2i-first-real-energy.md` |
| 2026-07-06 | third update / powermetrics telemetry | The powermetrics telemetry adapter and privileged sampling path were brought up, preserving raw plists and exposing the real sampling-rate constraints. | `docs/run_reports/2026-07-06-slice-2h-powermetrics.md` |
| 2026-07-06 | third update / pre-hardware hardening | Slice 2N closed the evidence-path hardening before real hardware: raw evidence retention, measured-window markers, rail validation, shared bundle reading, and post-hoc reduction. | `docs/run_reports/2026-07-06-slice-2n-pre-hardware-hardening.md` |
| 2026-06-12 | first/second updates / mock vertical slice | The mock-first harness reached an end-to-end auditable run path before hardware time: typed config to complete bundle, validation, reduction, and report. | `docs/run_reports/2026-06-12-phase-2-mock-vertical-slice.md` |

<!-- ADVISOR-PAGE-END -->

## Summary

JouleWise combines a reusable, typed measurement harness with a benchmark
defined by its frozen workload suite, run rules, and strict validator. It
measures the energy of LLM inference across heterogeneous local hardware. The
name nods to JouleSort and Splitwise: energy measurement is the spine of the
system. Under D-091, the capstone product is the trustworthy measurement
instrument itself: the paper leads with what the instrument can establish
about linearity, additivity, detection limits, and drift control.

Model comparisons, workload matrices, and disaggregated ("split") inference
studies demonstrate the instrument; they do not define whether the capstone
succeeds. Split inference — running prefill and decode on different machines
with the KV cache transferred between them — remains a valuable optional
demonstration when its hardware and feasibility gates clear. A crossover study
adds evidence, but it does not upgrade the capstone into a different product.

The frozen capstone headline, fallback claims, contribution ladder, and
minimum-viable stop-lines are now recorded in
`docs/contracts/capstone_scope.md`; that contract is the scope pointer for
reader-facing wording under the claims ladder.

The first working slice runs on a MacBook (Apple Silicon) with MLX as the
runtime and `powermetrics` as the power source, producing complete,
auditable run bundles. Further backends (NVIDIA + vLLM/llama.cpp, Jetson
Orin, Raspberry Pi + Hailo as a feasibility finding) plug into the same
adapter interfaces.

Research questions:

- **Q1**: Under what conditions (model size, prompt length, link speed,
  device pair) does splitting inference reduce total energy versus running
  monolithically on either device?
- **Q2**: How sensitive is the split's energy cost to interconnect
  bandwidth (1GbE vs 2.5GbE vs optional 10GbE) - where is the crossover?
- **Q3**: When splitting saves energy, what latency does it cost, and vice
  versa (energy-latency Pareto frontier)?
- **Q4** (added 2026-07-07, council C-003): What fixed-vs-marginal energy
  model `E = fixed + prefill(prompt_tokens) + decode(output_tokens)` does
  each target/model/quantization follow — and can split-run energy be
  predicted compositionally from monolithic coefficients plus transfer
  measurements?
- **Q5** (C-003/C-007): On one machine, do workload/model/quantization
  efficiency rankings stay stable as workload shape, model, and
  quantization change, or where do they flip? A cross-device ranking
  extension is hardware-gated.
- **Q6** (C-003; gated on the wall meter): Does the measurement boundary
  (platform rails vs AC wall power) change the conclusions?

Current question status, aliases, gates, and claim ceilings live in the
canonical live index, `docs/research_question_registry.md`. The curated bank
of further candidate questions and deliberately killed ones remains the
historical/deliberative record in `docs/research_question_bank.md`; the
measurement noise floor / detection limit is treated as the methodology
centerpiece rather than a numbered question.

The capability map by claim ceiling is reflected in
`docs/research_question_registry.md` (C-015), alongside the suite architecture
v2 and benchmark interop direction; the guaranteed-capstone stop-line is
recorded in the Phase 2 plan.

**Q4 architectural stress-test agenda (D-070).** Static batching,
speculative decoding / native MTP, MoE versus dense execution, quantization,
and reasoning-length variance are five stress tests of Q4's single
fixed-plus-marginal energy thesis, not five additional theses. The harness
must instrument every axis well enough to produce strict-valid L0 smoke
bundles, which establish only that the capability and evidence path work; the benchmark supplies the frozen workload suite, run rules, and
strict validator for claim-bearing runs. Per Ed's ruling, all five axes have
characterized-study commitments. Every study remains floor-gated and capped
at L2, the within-boundary comparative-result level; L3, a model fit tested on
held-out cells, is available only through Q4/AP-1's existing holdout machinery.
Window A remains first, and no AXI quiet-Mac characterization starts before
Window A completes. Static batching is the capstone scope; continuous
batching remains a post-capstone extension.

**Ranked extension-axis intake (D-075).** The later six-axis evaluation did
not create six more theses. It attached DSpark/DFlash break-even,
proposal-work, and contamination-control riders to the speculative-decoding
home; admitted an on-device MLX quantized-KV candidate and one named hybrid
pair; and attached cache/context, module-nonattribution, kernel, and backend
provenance riders to their existing questions. All admitted units remain
candidate work with earliest-phase tags, named forbidden upgrades, floor
gates, and an intake ceiling at or below L2. Unverified runtime, pair,
adapter, and device-fit questions remain explicitly NEEDS-WEB, and Ed retains
commitment and ordering authority under D-070.

## Status At A Glance

| Phase | Scope | Status |
|---|---|---|
| 1. Approval, feasibility, measurement design | contracts, methodology, hardware feasibility evidence | **in progress** — the Phase 1 exit checklist owns exact completion and external gates |
| 2. Harness, Mac vertical slice, homogeneous baselines | runnable instrument, live measurement path, per-target characterization | **in progress** — Mac vertical slice and analysis software are implemented; remote protocol pins remain PROVISIONAL; the state kernel and quiet-machine rules own execution eligibility |
| 3. Disaggregation, KV replay, interconnect sweep | optional split-energy demonstration study | planned (feasibility-first) |
| 4. Characterization and analysis | statistics, figures, claims audit | planned |
| 5. Presentation and submission | report, colloquium, reproducible release | planned |

## Capstone Artifact Map

| chapter/report-component | owning doc or deliverable | status | missing evidence |
|---|---|---|---|
| Background / related work | Phase 4 Stage 4.6, `docs/phase_4/related_work_draft.md` | drafted (11 verified sources) | background-chapter assembly and the Phase 4 exit pass |
| Measurement methodology | `docs/contracts/measurement_methodology.md` | complete | Phase 4 ratification may amend statistical details against observed variance |
| Harness / instrument | `joulewise/` | complete; pre-campaign software review cleared; C-028 closed | live execution eligibility comes from the state kernel; quiet-machine work also requires Ed and the clean hardware lane |
| Apple-Silicon characterization / homogeneous baselines | Phase 2 Slice 2M, `docs/phase_2/baseline_results.md` | Window A open; production shakedown closed; the first floor artifact is non-claim-bearing and its historical re-mint path is retired under D-117; quiet-Mac execution remains | P2-037 claim adjudication and the live state kernel govern the next baseline step; needs Ed + quiet Mac |
| Split-inference study | Phase 3 | planned | needs KV-feasibility spikes plus a real pairing, or the synthetic-transfer + analytical-composition floor |
| Results / limitations + claims audit | Phase 4 Stages 4.3-4.5 | analysis path implemented; governed calibration data exist | D-117's prospective alpha, beta, and gamma windows must establish fresh authority before any floor or downstream claim promotion |

Complete so far (all verifiable in the repository):

- A runnable harness: from a typed config, one command
  (`python3 -m joulewise run ...`) produces a complete, schema-valid,
  auditable run bundle and reduces it to energy and latency summary metrics.
  Deterministic mock adapters first proved the controller, bundle contract,
  and reducer mathematics without hardware; the same path now runs live on
  the Mac target. Implemented components include the bundle writer, controller
  lifecycle, reducer, static-HTML report generator, and the CLI verbs `run`,
  `validate-bundle`, `reduce` (post-hoc re-derivation of summary metrics from
  the recorded power trace and events), and `report`. Strict validation
  now also re-derives powermetrics traces from raw plist evidence, checks
  legacy additive-summary compatibility, and requires shape-valid
  provenance on new-era bundles. All bundle consumers read through one
  shared, tested read layer, which sharply reduces the risk of displayed
  numbers diverging from reported ones.
- Typed config and output schemas with validation, JSON-Schema export, and
  a CLI, plus the canonical suite run in CI on every push, including a mock
  end-to-end run and bundle validation. The command and CI output own the
  current result; reader docs do not copy its volatile count. Emitted configs
  round-trip their own published schema, and config hashes (run identity)
  are pinned by test.
- Adapter interface contracts (runtime / telemetry / transport), the run
  bundle artifact contract, and the measurement methodology (idle
  subtraction, measurement boundaries, clock synchronization, statistical
  protocol - highlights below).
- Evidence-shaped plans for every phase, a design-decision log whose index is
  mechanically checked against its decision bodies (with D-060 ratified by
  Ed); the log itself is the structural authority, and most entries record the
  alternatives considered), a risk register with
  an explicit descope ladder, and example configs for the Mac and mock
  targets.
- The complete Mac vertical slice: the MLX runtime adapter (2G), the
  `powermetrics` telemetry adapter (2H, parser pinned to a captured
  privileged sample, raw plists preserved verbatim in every bundle), and
  the flagship integration (2I) — three strict-valid repetition bundles
  from the M3 Max. Those bundles prove the live MLX, powermetrics, and
  evidence-custody path, but every P2-003 and FLAGSHIP-001 energy value is
  **VOIDED permanently for claim use** by the pre-repair time-anchor defect
  (D-078). They remain immutable instrument-history records, not preliminary
  results awaiting re-adjudication.
- The P2-042 frozen analysis manifest, P2-041 campaign verdict split,
  P2-037 contrast/claim engine, P2-040 reducer/gate remainder, P2-038
  production-uncertainty software path, and NV-GATE-2 code-now hardening.
  Reducer dispatch is frozen across the legacy and 0.3.x arms and current
  through 0.4.2. None of this promotes fixture-first NVIDIA evidence to live
  validation.
- The report's related-work survey draft (11 sources with verified
  citations and an honest positioning audit) and an off-machine iCloud
  Drive backup whose fresh restored bundles passed strict validation and
  were byte-identical to their sources.

Live remote-hardware validation has not started: NVIDIA/vLLM and Jetson
Orin promotion (2K/2L) remain gated on device access. The fixture-first
implementation and NV-GATE-2 software hardening are landed, but all remote
protocol pins remain PROVISIONAL until live
hardware contact; a P1-006 evidence checklist exists there. Code-level
specs are in `docs/phase_2/hardware_slice_implementation_guide.md`. The
mock-first core landed first by design, so measurement code is never
debugging the measurement harness and a live hardware integration at the
same time.

Waiting on external input (most of it does not block current software
work; P0-003's backup gate is satisfied, and the grading rubric/calendar
(P1-008) carries the provisional-contract fallback under ratified D-060):

1. NVIDIA / Jetson Orin device access evidence — the one hard gate left,
   for the remote-target slices 2K/2L. (The `nvidia_3050` in the
   architecture table is the owned always-available NVIDIA target; the
   3080 Ti is a separate, borrowed card used only for Phase 3's
   interconnect sweep.)
2. Calendar anchors: colloquium date, report deadline, and the 3080 Ti
   borrow window, to derive phase target dates.
3. Advisor scope confirmation (see the sanity-check note above) —
   finalizes model selection; deliberately deprioritized while all work
   remains harness-shaped and valuable under any scope.

Closed since the last revision: the comprehensive audit; AXI-SA's burst-decode
contract; SITE-02 D1/D2; the SPLIT-AP Part I pre-registration freeze;
AXI-SB's `supported` static-batch verdict with its Mac C5-2.2 leg; P2-038's
production-shaped live gate; and AXI-SC's `unsupported_for_joulewise` pinned-
runtime verdict. The later DSpark/DFlash MLX feasibility smokes and D-075
extension-axis intake are recorded without promoting an energy claim, and the
nine-bundle OLMoE/Qwen follow-on remains historical instrument evidence with
its energy values voided under D-078.
Window A's software gates are
satisfied, its first floor corpus is published, and the window remains open.
The floors are calibration thresholds rather than claim promotion: P2-037
adjudication remains pending because strict-valid collection and claim
readiness are separate gates; execution timing is governed by the live work-selection state
in `RUN_STATE.md`'s generated state-kernel region and still requires Ed plus a
quiet Mac.

## Architecture

```text
typed config
  -> controller
    -> transport adapter: local | ssh
    -> runtime adapter:   mock | mlx | vllm | llama.cpp (hailo: unsupported_workload — feasibility finding only)
    -> telemetry adapter: mock | powermetrics | nvidia-smi | jetson rails | wall meter
  -> run bundle (self-contained, on-disk source of truth)
    -> reducers (energy integration, idle subtraction, per-phase attribution)
    -> static report / notebooks / paper figures
```

Key elements:

- **Single controller, flexible transports.** `local` for one-machine
  runs; `ssh` for remote NVIDIA/Orin targets and split experiments.
- **Two adapter layers.** Runtime adapters answer how a model workload
  executes; telemetry adapters answer how power and thermal state are
  measured. They are independent, so any runtime can pair with any
  telemetry source.
- **A target is a composition** of transport + runtime + telemetry:

  | Target | Transport | Runtime | Telemetry |
  |---|---|---|---|
  | macbook_m3_max | local | mlx | powermetrics |
  | nvidia_3050 | ssh | vllm (llama.cpp-CUDA fallback) | nvidia-smi |
  | orin_nano | ssh | tbd | board rails (INA3221) |
  | pi5_hailo | ssh | hailo - unsupported (verdict 2026-06-12) | wall meter |

- **Every run writes a self-contained run bundle**: normalized config,
  device/environment metadata, timestamped event log (lifecycle + phase +
  token events), raw power trace, backend-native raw telemetry preserved
  verbatim, logs, model outputs, and reduced summary metrics. Summary
  numbers are always derived, re-derivable artifacts; the raw bundle is
  the source of truth.
- **Typed schemas** (Python dataclasses, standard library only in the
  core) validate configs and outputs and emit JSON Schema documentation.
- **Unsupported is a result, not a crash.** Infeasible
  hardware/model/runtime combinations return structured failure codes
  (`did_not_fit`, `runtime_unavailable`, `telemetry_unavailable`, ...)
  and still produce complete bundles - hardware applicability is itself
  reportable data (this is how a negative Hailo verdict stays a finding).
- **Dashboard v1 is a read-only run browser**, generated as static HTML
  from bundles (run table, per-run pages, power traces with phase
  shading). It has no orchestration role.

## Measurement Methodology Highlights

Unless a figure explicitly states otherwise, JouleWise uses gross measured
energy within the named measurement boundary as the headline basis. Gross
energy retains the idle, model-residency, and runtime overhead present during
the measured interval, so comparisons across devices, configurations, and
split versus monolithic execution use gross energy. Idle-subtracted energy is
reported separately as a within-device secondary view of activity above the
measured idle baseline; it is not used to rank devices or configurations. In
Q4, the fixed term is estimated from the gross-energy workload sweep and is
not set equal to measured idle energy.

This reporting choice follows Dr. Rivoire's advisor review, as recorded in
D-067: subtracting idle penalizes energy-proportional devices and rewards
high-idle ones; for split runs, subtracting both nodes' idles deletes exactly
the cost that the Q1 crossover question adjudicates.

- **Dual-basis capture.** Every eligible measured request records gross and
  idle-subtracted energy plus idle variance; the reporting rule above changes
  no stored evidence (D-067).
- **Measurement boundaries are named, not assumed.** Each telemetry
  backend measures a different physical boundary - powermetrics: Apple
  SoC subsystems (CPU+GPU+ANE); nvidia-smi: GPU board only; Jetson rails:
  module input; wall meter: full system AC. Within-target comparisons are
  the primary claim type; cross-target comparisons always state the
  boundary difference, calibrated against the wall meter where available.
- **Uncertainty is quantified.** Headline comparisons use n>=5
  repetitions with mean, standard deviation, and 95% t-intervals;
  outliers are flagged (never silently dropped); raw points appear in
  every figure. Differences are claimed only from the confidence
  interval of the predeclared paired/block difference or named model
  contrast — never from marginal-interval separation — with the D-053
  three-way wording rule (below-floor: not resolvable; above-floor
  non-directional: unresolved; equivalence only via a predeclared gate).
  Thermal state is controlled with an idle-power-recovery gate between
  repetitions.
- **Multi-node clock discipline.** For split runs, per-node clock offset
  is bounded with controller-mediated marker events and recorded;
  cross-node intervals shorter than the bound are flagged rather than
  trusted.
- **Measurement quality is first-class data**: requested vs observed
  sampling rate, dropped samples, idle variance, thermal drift, telemetry
  source - all in every summary.

## Experiment Plan

**Homogeneous baselines (Phase 2).** Per target and model: a workload
matrix spanning prefill-heavy, decode-heavy, and balanced profiles
(prompt 128-4096 tokens x decode 64-512), n=5, producing energy/token and
energy/request with intervals - and reproducing the qualitative
prefill/decode power asymmetry that motivates disaggregation.

**Disaggregation (Phase 3), feasibility-first.** KV-cache portability is
the project's central technical risk, so the phase is a ladder where each
rung is publishable even if the next fails:

1. *Synthetic transfer microbenchmark* (guaranteed): move KV-sized
   payloads between nodes with both-end power sampling - transfer energy
   and time vs payload size vs link speed, independent of any LLM
   runtime's cooperation.
2. *Offline replay* (primary): persist the prompt cache on the prefill
   node, transfer the file, resume decode on the decode node - same
   pinned runtime on both ends. Per-runtime feasibility spikes (mlx-lm,
   llama.cpp including cross-machine portability, vLLM time-boxed) run
   before any borrowed-hardware scheduling.
3. *Live split* (stretch): streamed KV during the run; explicitly
   droppable without harming the study.

Payload sizes are analytically predictable (2 x layers x kv_heads x
head_dim x 2 bytes per token, fp16), which drives experiment design - for
a 2048-token prompt: a 1.5B-class model ~56 MiB (~0.5 s at 1GbE), an
8B-class model ~256 MiB (~2.3 s at 1GbE). At 1GbE, mid-size-model
transfer time is the same order as prefill time on weaker devices -
exactly the regime where an energy crossover can exist; the sweep spans
prompt lengths and link speeds accordingly.

**Analysis (Phase 4).** Aggregation over validated bundles with an
exclusion log (no silent data drops); a deterministic figure pipeline
(every report figure regenerates from a script); a claims-to-evidence
index (every quantitative claim traces to figure -> script -> raw
bundles); a sensitivity audit checking that headline effects exceed their
confidence intervals.

## Phase Plan Detail

Each phase has a step-by-step plan and an evidence-gated exit checklist
in the repository; a phase closes only when every required item has
recorded evidence or a documented blocker.

- **Phase 1** - `docs/phase_1/`: lock contracts and methodology (done);
  gather feasibility evidence: advisor scope, Mac telemetry permissions,
  wall-meter decision, network topology for the sweep, Hailo verdict,
  NVIDIA/Orin access, calendar mapping.
- **Phase 2** - `docs/phase_2/`: bundle writer -> mock adapters ->
  controller -> reducer -> one-command run (all hardware-independent,
  exact-arithmetic tests) -> then the real Mac slice (MLX + powermetrics,
  repeated with variance) -> remote targets as access permits ->
  homogeneous baselines.
- **Phase 3** - `docs/phase_3/`: feasibility spikes -> split-run config
  schema -> transfer microbenchmark -> offline-replay splits with
  per-stage energy decomposition (prefill / transfer / deserialize /
  decode) -> interconnect sweep -> crossover dataset.
- **Phase 4** - `docs/phase_4/`: statistics ratification, aggregation,
  figures F1-F12 (baselines, traces, phase asymmetry, split decomposition,
  crossover curves, Pareto frontier, interconnect costs, measurement
  quality), claims index, results + limitations draft, background /
  related-work draft (new stage 4.6 — the report's background chapter now
  has an owner).
- **Phase 5** - `docs/phase_5/`: verified README quickstart, backend
  extension guide (verified by a shipped tutorial adapter), sample
  bundles, dataset freeze with hash manifest and release tag, colloquium
  slides, final report.

## Evolution From The Original Architecture Sketch

The project began from the "Energy Benchmark Architecture And Expanded
Plan" sketch. Its architecture survives intact; implementation thinking
has been refined in documented ways (full rationale in
`docs/decision_log.md`):

| Original sketch | Current position | Why |
|---|---|---|
| Configs YAML/JSON; bundle stores `config.yaml` | JSON now; bundle stores normalized `config.json`; YAML deferred until authoring pain is real | zero-dependency core; sorted-key JSON gives stable config hashing for aggregation (D-001, D-007) |
| "Likely Python + Pydantic" schemas | stdlib dataclasses with the same contract; Pydantic port possible later | Phase 1 runs with no installs; semantics unchanged (D-009) |
| Mac MLX slice implemented first | mock vertical slice first, Mac immediately after | the harness is proven with exact-arithmetic tests before real telemetry can confound it; Mac remains the first real backend (Phase 2 plan) |
| Dashboard file-backed; "DuckDB/SQLite if browsing gets slow" | static HTML generator; analysis aggregation via CSV + pandas in Phase 4; no DB planned | smallest sustainable tool that serves the two real uses: sanity-checking runs and showing progress (D-006) |
| Offline KV replay before live disaggregation | same, hardened into a three-rung feasibility ladder with per-runtime spikes and a same-runtime rule | KV tensors are not portable across engines; cross-runtime transfer (e.g. vLLM-prefill -> MLX-decode) is out of scope; heterogeneous *hardware* pairs use a portable runtime where its backends allow, pending an explicit portability spike (D-015) |
| GPU-to-Apple split experiments listed directly | pairings are planned only after spike verdicts; synthetic transfer sweep guarantees the crossover dataset either way | converts the project's largest feasibility risk into a bounded one (R-004, R-005) |
| (not covered) | measurement boundaries, multi-node clock discipline, controller co-residency mitigation, statistical protocol | added rigor required for defensible cross-device energy claims (D-003, D-013, D-014, D-018) |

Verdict from the 2026-06-09 audit: the sketch remains coherent; nothing
in it has been contradicted - the changes above are refinements with
recorded rationale, and the repository's plans are the maintained,
authoritative version of it.

## Risks And Minimum Viable Outcome

Top risks (full register with triggers and fallbacks in
`docs/risk_register.md`):

| Risk | Posture |
|---|---|
| KV persist/resume unsupported in a runtime (esp. vLLM) | spikes before hardware scheduling; llama.cpp fallback; synthetic-transfer floor + analytical composition keeps the study publishable |
| Cache files not portable across machines/backends | explicit cross-machine spike; fallback to same-platform pairs; portability finding is itself reportable |
| Schedule vs fixed academic deadlines | every phase has a hardware-independent floor; explicit descope ladder |
| 3080 Ti borrow window slips | borrow time is execution-only against a rehearsed runbook; pairing droppable |
| No wall meter | within-target claims unaffected; cross-target claims carry the stated boundary caveat |
| Advisor approval delay | all current work is harness-shaped and valuable under any scope |

Minimum viable outcome (worst-case floor; still a complete, defensible
capstone if reached):
the trustworthy measurement instrument + a governed Apple-Silicon
characterization + demonstration studies that clear their own gates — honest,
measured, and reproducible. Split and interconnect work may add a demonstration
without becoming a completion requirement.

## Timeline

Dates pending (this is an explicit ask): colloquium date, report
deadline, borrow window. Once known they anchor `docs/milestones.md` and
phase target dates are derived backwards (slides want frozen figures >=1
week ahead; the report wants its claims audit >=1 week ahead). Until
then, the dependency structure is the schedule: Phase 4 is deskwork and
serves as the buffer; hardware-gated steps are scheduled around access
windows with desk work filling gaps.

Known: the Mac authorization gate closed 2026-07-06 (privileged sample
captured, scoped sudo rule installed); remote-device access (NVIDIA,
Orin) is the remaining hardware gate. Work paused 2026-06-13 to
2026-07-04 (planned break, recorded in `docs/milestones.md`).

## Deliverables At Completion

- The JouleWise repository: harness, adapters, tests, CI, extension
  guide, README quickstart that a new user can run in minutes.
- The dataset: raw run bundles + hash manifest, frozen and tagged, with
  every figure regenerable by script.
- Demonstration studies showing what the instrument can and cannot resolve,
  with uncertainty, limitations, and hardware-applicability findings
  (including negative verdicts); split inference is one optional study.
- Final report and colloquium presentation, every quantitative claim
  traceable to raw data.

## Repository Map (for verification)

| Where | What |
|---|---|
| `README.md` | entry point and quickstart (grows in Phase 5) |
| `AGENT_PLAN.md` | phase index and acceptance criteria |
| `docs/phase_N/phase_N_plan.md` + `_exit_checklist.md` | per-phase steps and evidence gates |
| `docs/contracts/` | measurement methodology, run-bundle layout, adapter contracts |
| `docs/decision_log.md` | every design decision with alternatives considered |
| `docs/risk_register.md` | risks, triggers, mitigations, descope ladder |
| `docs/milestones.md` | calendar map |
| `docs/run_reports/` | dated work logs with commands and outcomes |
| `joulewise/`, `tests/` | the harness package + canonical test suite; the command and CI output own its current result |

## Process Note

The machinery exists to protect measurement claims from unchecked summaries,
stale assumptions, and review-induced drift.

This project is developed by a human researcher directing a multi-agent AI
system that he designed and iteratively engineered during the project. The
orchestration is a second, deliberate engineering effort alongside the
measurement harness and benchmark, and it is now a substantive project result
in its own right.

The full description lives in `docs/orchestration.md` (the loop, the
roles, the artifact system, and how the topology itself evolved under
its own review machinery); this section is the summary.

**The division of labor.** Ed sets the research direction, the
methodology standards (the decision log's non-negotiables: raw-evidence
bundles, dual-basis capture with gross-energy headlines, named measurement
boundaries, and no unauditable claims), plus the hardware and access
decisions. He also sets the *process policy*: every rule below exists because
he observed a failure or opportunity and issued a standing instruction. The AI
staff executes that policy. The designated lead agent is the final reviewer
and single point of accountability for decomposition, design adjudication,
every final diff gate, live verification, merges, and bookkeeping. Independent
implementation and review agents handle work against pinned specifications,
adversarial review lenses, test writing, and fresh-instance test auditing;
specialist agents handle bounded sweeps. Cross-model review is load-bearing by
design because the attributed catch record shows the models and review layers
catching different classes of defect.

**The machinery, briefly.** Independent tasks run as parallel git
worktrees, and the lead drives each stream's implementation and review pipeline
directly. A signed cross-model meta-review produced this topology; a full
session then validated it with zero coordination stalls. The evolution is
traced in `docs/orchestration.md`.

Every implementation passes through a layered pipeline. The implementer first
argues the design trade-offs before coding. Fresh reviewers then examine the
change from distinct angles, and the lead records a disposition for each
finding. A separate round adds tests; a writer never audits their own tests;
the lead reviews the final diff; and the lead alone performs live verification
on real hardware. That final layer is never delegated because it has repeatedly
caught blockers whose own tests encoded the same wrong assumption as the code.

Merges add a pre-merge oversight pass by fresh reviewers with distinct angles.
They also carry a standing *final-head rule*: any commit that lands after the
last review round gets one more fresh review before merge. The rule's first
application caught a crash path in a "trivial" late fix. After parallel streams
merge, a dedicated integration review looks for cross-stream defects that no
per-stream review can see; it found two interaction defects on its first outing
and two more on its second.

An event-driven review council convenes for contract-bearing work. Per Ed's
instruction, the council records its *deliberations*, not only its verdicts.
The council log preserves positions, the reasoning exchanged, who prevailed
and why, and overridden dissents, so a future reader or model can reconstruct
why each decision was made.

**The paper trail (each claim traceable to its evidence home; the
external re-reduction demonstration is still pending).** Each fact has one home:
`docs/decision_log.md` — the binding design decisions (the log is the count authority), most recording
alternatives considered and revisit conditions; `docs/council_log.md`
— the deliberation record; `docs/stream_logs/` —
per-stream decision ledgers committed *with* the code they justify
(wrong decisions are superseded in place, never erased);
`docs/run_reports/` — one record per session with verification
evidence, a per-review-layer catch table, and a delegation-calibration
ledger (outcomes assigned by the lead after the gate, never
self-reported; prompt-defects separated from model-defects). The whole
loop is self-instrumenting: every review layer's unique catches are
attributed and tallied, and a layer that stops earning its keep is
dropped by its own evidence rule (one already has been). Delegation
boundaries move on calibration evidence, not intuition. Lessons are
folded into the process playbooks the same session they are learned —
measurably: one failure mode recurred five times before its fix was
distilled, and zero times after. The loop even reviews itself: a
meta-review consensus (C-009) redesigned the coordination topology, and
the next session (C-010) validated the redesign with a zero-stall run.

**What one day of this looks like (2026-07-07).** Five implementation
streams plus a repo-wide test audit ran concurrently: statistical
uncertainty, contamination detection, deep DVFS telemetry, campaign
automation, and a KV-cache size model. All five merged the same day;
the test suite grew 254 → 369; the layered review recorded thirteen
attributed catches including three blockers that no single reviewer
would plausibly have found together. One blocker surfaced only when the
real CLI was run against code whose own tests were green, because the
tests encoded the same wrong assumption as the code.

**How the scope grew.** The project began as an architecture sketch for
"measure LLM inference energy on edge hardware." Contracts-first
engineering turned that into an auditable instrument: typed configs,
self-contained evidence bundles, a strict re-reduction validator. The
mock vertical slice proved the math without hardware; the Mac slice then
proved the live adapter and evidence path. Its pre-repair energy values,
including the flagship comparison, are **VOIDED under D-078**; discovering
and repairing that attribution failure became part of the instrument's
story rather than a result to defend. This week the
instrument gained the statistical and
forensic machinery above, and a steelmanned, devil's-advocated research
agenda of 31 tiered questions — 16 answerable on the current hardware
alone (`docs/research_question_bank.md`). The pattern throughout:
capability first, claims only when the instrument can defend them.

**And the most recent day (2026-07-07/08).** Four checkpointed streams
were resumed, completed, and merged in one session: the integrity/
provenance overhaul (all 31 audit-pinned defects fixed; strict
validation now re-derives the power trace from raw evidence), the docs
package, the KV-cache replay feasibility verdict, and the complete
fixture-first NVIDIA stack. The layered review recorded ~30 attributed
catches, including two blockers no implementer's tests could see (a
provenance hash that did not prove the actual generation input; a
validation-gate bypass via mutable metadata), two pinned wire contracts
overturned by review before they could ever touch hardware, and one
fabricated-evidence defect caught only at the lead's diff gate. The
suite went 415 → 546 tests with zero expected failures, and the lead
never wrote implementation code and never skipped a gate.

**Where to look.** `docs/orchestration.md` is the process description.
`docs/council_log.md` is the deliberation record — C-006
is a full orchestration trace of the five-stream day; C-009/C-010 are
the topology meta-review and its validation; C-011 is the critique
counter-review. `docs/decision_log.md` holds the binding design
decisions with alternatives considered (the log is the count authority).
`docs/run_reports/` narrates each working session, with per-layer catch
tables and the delegation-calibration ledger. The executable
orchestration playbooks live outside this repository as reusable
skills (council, delegation, multi-stream worktrees, adversarial
review, and a top-level operation-loop that sequences them), so the
machinery survives this project and transfers to the next one.

## Maintenance Of This Document

Updated at phase transitions and whenever advisor-visible state changes
(a gate closes, a verdict lands, the schedule moves). Volatile work-selection
facts stay in the state kernel, verification results stay in command/CI output,
and decision structure stays in the checked decision-log index. A
front-facing change also refreshes `docs/site/DRIFT.md`; Ed alone regenerates
and deploys the site (D-068).
