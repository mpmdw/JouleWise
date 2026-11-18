# Legacy JouleWise Run State
Archived from commit `d934178b9bd836162122db941c64d185593fa554`.
The body holds the former pre-item introduction and moved legacy bytes in source order.

This file is the single running pointer for the project: the one doc to
read to get back here. Session records live in `docs/run_reports/` and
`docs/process_traces/`; deliberation lives in `docs/council_log.md`;
policy lives in `docs/decision_log.md`. Do not create a dated restart doc;
update this file instead.

**Current pointer: read the top numbered item first.** That is the
highest-numbered item; from item 168 on, items run newest first and start
right after item 167 below. [`CANONICAL.md`](CANONICAL.md) is the tool map:
the one current tool or document per job. [`docs/ARCHIVE.md`](docs/ARCHIVE.md)
says how to get back files removed from `main` in the 2026-11-06 prune.

**Block-5 history: the magistrate's hand-off of 2026-10-10 08:40 PDT (activation cbe4230e).** It was the step list for block-5 collection, which closed on 2026-10-12 (item 31). The numbered items below grew from it; the current state is the top numbered item, not this block.

What happened. BETA attempt 1 (`v5-b5-beta-a1-20261010T0742Z`) ran its whole chain; the pinned harvest gave it one window-removing code, `neg8.screen_failed` (`harvest.json` sha256 `f0d72323b67d075db29a5c136d087222284a6d4651d130549f9dbd5a82d6ec7d`). No physical measurement removed it. One end reference (a short run of a fixed small workload, used to check that the machine did not drift between a window's start and end) was aborted at run time; the chain ran its spare; the spare left no result directory; and the sealed program that writes the window's verdict then recorded none of the window's stage lists as its source. The registered harvest rule re-runs the drift check only on the references that verdict names, so the check was never run, although two start and two end references survive, which is enough. Records: `docs/process_traces/2026-10-block5/seal2-beta-a1-window.md`, `seal2-beta-a1-consult.md`.

What was ruled (cold gate, registration section 10; `docs/process_traces/2026-10-block5/sources-erratum/RULING.md`, last line `RULING: ADMIT-WITH-CORRECTIONS`). **Erratum 2** (`sources-erratum/ERRATUM.md`, sha256 `b8510545…188a`, pinned in Addendum 3 step 1 of the seal record) lets the harvest take the reference list from the runs root's authenticated stage lists in exactly that state. It is prospective: it governs only attempts whose t0 is later than `2026-10-10T16:30:00Z` (epoch 1791649800). It is **not** applied to BETA attempt 1, which stays not claim-usable, kept and disclosed, never analysed, and is never harvested again for a deciding record. Nothing a window reads changed: same clone, same claim head, same seal commit, same registration digest.

B5-ARM-RELEASED: beta gamma

(The line above is read by a program. ALPHA has its claim-usable window and is never armed again. BETA is released again since 2026-10-11 10:50 PDT (item 25) and GAMMA since 11:10 PDT, when the gate of item 26 was executed: `docs/process_traces/2026-10-block5/trigger-erratum/harvest-pin4-gates.md`, last section.)

Differences from the brief, added to the eight of the block below:
<!-- RUN_STATE LEGACY ITEMS below: prose, not typed; cutover 405 -->
<!-- BEGIN GENERATED: state-kernel run-state-intake -->
## ACTIVE_STOP_CARD

Status: NONE — no stop card is active. Stop-card authority: D-050 / D-063 ([decision log](docs/decision_log.md)).

## Active Global Work-Selection Gates

NONE — no global work-selection gate is active.

## Restart By Machine-State Lane

Source of truth for work selection: [state kernel](docs/process/state_kernel.json) (updated 2026-09-25). Latest report: [Activation 152c9255 record: acceptance ruled (Interactive+v3); claim-gate wiring, reducer and J/correct floor ruled; CG-1 accuracy-term amendment; PR-L/PR-R/PR-0/A292 in review](docs/process_traces/2026-09-25-activation-152c9255/00-activation-record.md).

### [ED-EXTERNAL]

- READY — E1 `ED-DATES-01`: Obtain the authoritative final-report and colloquium dates, record them in the milestones, and derive the internal cut dates.

### [QUIET-MAC]

- READY — Q2 `V5-G2A-PREFILL-PROBE-01`: Run the first quiet-machine evening for G2-a: bracket the four 512, 1024, 2048, and 4096 prefill probes, collect at least five Qwen3-1.7B members per rung, record the Qwen3-8B non-gating probes, and preserve the selector input.

### [AGENT]

- CONTINUE — A88 `NIGHT-REHEARSAL-01`: After the watchdog install handoff, run one fresh REHEARSAL_STUB night through the installed LaunchAgent and night-driver courier before any real plan, then send the stage-1 email before the first diagnostic plan is armed.
- CONTINUE — A139 `PAPER-CUSTODY-SEAM-01`: Finish the shared paper-custody read seam that wraps the existing authentication session, derives all bindings from a clean-Git supply map, replays validators, and returns only family-specific frozen verified objects.
- CONTINUE — A149 `DECISION-LOG-RATIFY`: Install the ruling-43 addenda for D-078, D-083, D-165, D-166, and D-161 plus the new D-174 submission scope freeze in the decision log.
- CONTINUE — A153 `D166-PROMPT0-01`: Move both decode comparison arms to prompt 0, beginning with a dependency census and ending with explicit supersession, regenerated custody, and the clone proof.
- CONTINUE — A256 `EVIDENCE-NIGHT-ENTRY-01`: PR 1: deliver tracked python -m joulewise.evidence_night prepare --kind quiet_predicate_evidence --t0 next [--head H] that clones and builds the locked venv at H, authors the v2 plan and renders the wrapper at staging, runs the real installer render-only FROM the clone, resumes idempotently on sealed bytes, and STOPS at the notice boundary. Add a thin evidence lifecycle façade (render/probe/install/uninstall/verify) delegating to existing installer machinery, not a second installer; tests/test_evidence_night.py, extended tests/test_evidence_arm_sequence.py, docs/contracts/evidence_night_entry.md and the handbook/runbook checklist replace per-night script copies. PR 2 later, after lifecycle decision F3: notice → wait → veto → publish → install orchestration through a narrow transport adapter, plus census argv and producer identity provenance in the watchdog’s census events, separately reviewed.
- CONTINUE — A292 `HEADLINE-REDUCER-SEALED-01`: Build the scored reducer, which reads the sealed capture roster and per-problem score records, attributes gross power energy to each executed problem block, and produces only evidence supported by the recorded captures. It starts after the packer has a gated roster, so the reducer cannot invent missing attempt or score identity.
- CONTINUE — A303 `HEADLINE-POWER-01`: Decide n_acc per level under Ed’s O-18/E4 delegation before AP-5M v5 registration freezes.

<!-- END GENERATED: state-kernel run-state-intake -->
