# JouleWise: Project Status, Plan, And Architecture

Capstone advisor view · 2026-11-21

Earlier advisor updates and probe-era context are in [Project Status History](docs/project_status_history.md).

This document promises sequence, not dates. Live status is in `RUN_STATE.md`.

*Prefill* processes the prompt and *decode* generates the answer.
The *detection floor* is the largest false difference the admitted measurement system can produce. [Measurement terms](docs/glossary_measurement_terms.md)

## Current Claim And Scope

JouleWise measures the energy and latency of local language-model inference and reports the limits of each measurement.
The released Qwen3 comparison concerns gross phase energy per request on the M3 Max processor rails, using MLX, `powermetrics`, the registered prompts, and the registered output policy. [Block 5 claim scope](docs/analysis/b5/RESULTS.md#L307-L329)
It is not wall or whole-machine energy, and nothing is claimed about other machines, prompts, prompt lengths, models or a scaling law.

## Measured Evidence

- **Block 5, released 2026-11-08.** Qwen3-8B used more gross phase energy per request on the processor rails than Qwen3-1.7B in both decode and 2048-token prefill.
  Both contrasts cleared their detection floors, survived Holm correction, and reached comparative claim level L2 in the same interleaved session.
  The separate-session per-model cells are L1 instrument results, reportable side by side.
  Phase attribution was reported without a measured instrument phase-accounting check. [Contrasts, decision intervals, and floors](docs/analysis/b5/RESULTS.md#L62-L93) · [Reported cells](docs/analysis/b5/RESULTS.md#L126-L139) · [Registered limitation](docs/analysis/b5/RESULTS.md#L325-L334)
  The registered D-165 dominance test returned branch B, so the dominance statement is withheld; this is the pre-registered non-dominance outcome. [Dominance test](docs/analysis/b5/RESULTS.md#L330-L334)
- **Block 6, released 2026-11-13.** Both contrasts **replicated** under the registered rule: each of the three counting contrast sessions gave the same outcome word and the same sign as Block 5.
  "Replicated" is the registered word for that agreement; it is not a new test and carries no new interval, and any claim level is the one reached in each session separately.
  The replication is across sessions and days on the same machine, not across machines. [Release record](docs/registrations/block6_release_record.md) (`RUN_STATE.md` item 312) · [Paper 1 §6.8](docs/paper/paper1/paper1.md#68-replication)

## Gate Matrix

| Work | Gate |
| --- | --- |
| Paper 1 | Fill remaining placeholders from the named issued artifacts after their respective releases. [Fill index](docs/paper/paper1/fill_index.md#L9-L12) |
| ALIGN v4 qualification | The lead issues qualification items after freeze 2. (`RUN_STATE.md` item 462) |
| ALIGN v4 W1 | The lead must promote the reviewed candidate before issuing a W1 arm instruction. (`RUN_STATE.md` item 462) |

## Artifact State

- **Paper 1** is the capstone manuscript draft and reports the primary and replication blocks side by side. [Paper 1 §6.8](docs/paper/paper1/paper1.md#68-replication) · [Submission plan](CANONICAL.md#L144)
- **BYTES** committed its rival prediction lines on 12 November 2026; the seven held-out models remain sealed. [BYTES status](README.md#L93-L99)
- **ALIGN v4** (the energy-tripwire protocol) is in registration and calibration; no outcome has been opened.
  The R1 rehearsal is finished (`RUN_STATE.md` item 459), and instrument-stability sessions are running on the measurement Mac.
  Live state is in `RUN_STATE.md` and is not copied here. [Campaign status](README.md#L105-L111)

The controller composes adapters for moving data, executing the model, and
collecting telemetry, then writes self-contained run bundles containing the
normalized configuration, environment and device identity, workload events,
raw power readings, outputs, and derived summaries. Reducers and reporting are
downstream and read-only with respect to raw evidence.

## Advisor Decisions And Risks

The evaluator acceptance bar, the colloquium date and the final-report deadline are not yet recorded (task `ED-DATES-01`). This page infers none of them. [Academic calendar](docs/milestones.md#L9-L16)
Advisor approval was not required to open the Qwen3 transaction under D-171.

## Next Milestone

Complete the eligible artifact-backed fills for the Paper 1 capstone submission (Ed's decision E1, `RUN_STATE.md` item 256b: mid-December). [Submission plan](CANONICAL.md#L144) · [Fill index](docs/paper/paper1/fill_index.md#L9-L12)
On the measurement track, the stability sessions continue while qualification and W1 wait on the gates above. No date is recorded for either.

## Evidence Links

- [Claims Status](CLAIMS_STATUS.md) and [Block 5 release](docs/analysis/b5/RESULTS.md)
- [Live project state](RUN_STATE.md) and [current campaign pointer](docs/process/CURRENT.json)
- [Canonical map](CANONICAL.md) and [research agenda](docs/research/AGENDA.md)
- [Work-selection kernel](docs/process/state_kernel.json)
- Ed alone chooses whether to dispatch manual regeneration or deployment. [Retired status-site reference](docs/site/DRIFT.md)
