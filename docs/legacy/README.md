# Historical archive

## Why this folder exists

These are historical records: raw transcripts of past automated work sessions, superseded plans, finished per-stream logs (records for individual work assignments), and terminal records of stopped work. They are kept for audit and provenance—so that any claim in the paper can be traced back to what was actually done—but are no longer part of the day-to-day reading surface. This folder was created to shrink what a reader has to wade through, not to hide anything.

## How to find something that used to be somewhere else

The rule is mechanical and has no exceptions: a file that used to be at `docs/X` is now at `docs/legacy/X`, and a file that used to be at the repository root is now at `docs/legacy/root/`.

Paths below start at the repository root. For example:

- `docs/instrument-v2-lessons.md` → `docs/legacy/instrument-v2-lessons.md`.
- `STOPPED-FCM01.md` → `docs/legacy/root/STOPPED-FCM01.md`.

Old links inside historical documents were not rewritten because rewriting a historical record to match a new layout would alter the record, and the record is the evidence.

## Nothing was deleted

309 files moved, totaling 83,121,775 bytes (79.27 MiB, where 1 MiB = 1,048,576 bytes); every byte is preserved, and every move is a Git rename, so `git log --follow` still works.

## What moved

Counts and sizes describe the files moved in `f6aed467`, excluding this new guide; sizes are file bytes, not disk allocation.

| Old path | New path | Files | Size | What it is |
|---|---|---:|---:|---|
| `FREEZE-FCM01.md` | `docs/legacy/root/FREEZE-FCM01.md` | 1 | 3,796 bytes | Record of a work freeze after a proposed calculation failed review. |
| `STATUS.md` | `docs/legacy/root/STATUS.md` | 1 | 1,496 bytes | Finished work-stream status and its handoff instructions. |
| `STOPPED-FCM01.md` | `docs/legacy/root/STOPPED-FCM01.md` | 1 | 2,027 bytes | Final record of stopped work on that calculation. |
| `docs/advisor/` | `docs/legacy/advisor/` | 1 | 7,730 bytes | A past session brief for the project advisor. |
| `docs/critique_text_extract.txt` | `docs/legacy/critique_text_extract.txt` | 1 | 23,063 bytes | Plain-text extraction of a project critique. |
| `docs/evidence/` | `docs/legacy/evidence/` | 4 | 5,582 bytes | Saved verification results and test logs. |
| `docs/instrument-v2-lessons.md` | `docs/legacy/instrument-v2-lessons.md` | 1 | 64,132 bytes | Lessons for a possible second version of the measurement tool. |
| `docs/process_traces/2026-07-13-bridge-v11.manifest.jsonl` | `docs/legacy/process_traces/2026-07-13-bridge-v11.manifest.jsonl` | 1 | 10,871 bytes | Index of automated-session invocations and their outputs. |
| `docs/process_traces/2026-07-26-prereg-clock-mitigation.md` | `docs/legacy/process_traces/2026-07-26-prereg-clock-mitigation.md` | 1 | 8,742 bytes | Past plan for handling clock changes during measurements. |
| `docs/process_traces/2026-08-08-t1-consistency-sweep.md` | `docs/legacy/process_traces/2026-08-08-t1-consistency-sweep.md` | 1 | 12,770 bytes | Past check for disagreements among project documents. |
| `docs/process_traces/RESUME-2026-07-27.md` | `docs/legacy/process_traces/RESUME-2026-07-27.md` | 1 | 11,259 bytes | Past session restart instructions. |
| `docs/process_traces/RESUME-2026-07-28.md` | `docs/legacy/process_traces/RESUME-2026-07-28.md` | 1 | 11,927 bytes | Past session restart instructions. |
| `docs/research_question_coverage-2026-08-28.md` | `docs/legacy/research_question_coverage-2026-08-28.md` | 1 | 55,643 bytes | Past mapping of research questions to planned measurements and retained evidence. |
| `docs/strategy/2026-08-07-paper-portfolio/` | `docs/legacy/strategy/2026-08-07-paper-portfolio/` | 52 | 27,777,245 bytes | One dated round of superseded paper-direction proposals, their reviews, and the planning discussion that ranked them. The other nine files under `docs/strategy/` stayed in place. |
| `docs/test_audit_2026-07-07.md` | `docs/legacy/test_audit_2026-07-07.md` | 1 | 15,552 bytes | Past test-suite audit. |
| `docs/process_traces/<dated directory>/` | `docs/legacy/process_traces/<same name>/` | 240 | 55,109,940 bytes | Raw automated-session transcripts, prompts, reviews, decisions, and results. |

Archived trace directory names (each sits under `docs/legacy/process_traces/`):

  - 2026-07-13-bridge-v11
  - 2026-07-14-c033-axi-consult
  - 2026-07-16-axi-sb-live-probes
  - 2026-07-16-axi-sd-web-verification
  - 2026-07-16-device-list-brief
  - 2026-07-17-axi-sc-live-probes
  - 2026-07-17-dspark-dflash-smoke
  - 2026-07-17-exploratory-block
  - 2026-07-17-extension-axes
  - 2026-08-03-calbracket-b1-gate
  - 2026-08-03-d111-backfill
  - 2026-08-03-winB-reeval-stop
  - 2026-08-04-calbracket-collision-consult
  - 2026-08-04-calbracket-integration-collision
  - 2026-08-04-incident-state-forgery
  - 2026-08-04-quiet-guard-spec
  - 2026-08-04-t3-char-pair
  - 2026-08-05-d079-issuance
  - 2026-08-05-d113-rigor-consult
  - 2026-08-05-t3-amend
  - 2026-08-06-d079-issuance-coldgate
  - 2026-08-06-d110-remint-fork
  - 2026-08-06-qg-census-consult
  - 2026-08-07-d117-plan-freeze
  - 2026-08-07-d117-u-units
  - 2026-08-07-meta-sweeps
  - 2026-08-07-night-hardening
  - 2026-08-07-prefill-feasibility
  - 2026-08-07-u2-coldgate
  - 2026-08-08-d127-autonomous-loop
  - 2026-08-08-recovery-exits-escalation
  - 2026-08-08-trust-fixture-substrate
  - 2026-08-08-trust-scoping-escalation
  - 2026-08-11-5c-readiness-contract
  - 2026-08-11-fcm-coldgate
  - 2026-08-11-staged-contracts
  - 2026-08-12-calexits-mutation-consult
  - 2026-08-12-evauth-coldgate
  - 2026-08-12-item1-margin-consult
  - 2026-08-12-mintvocab-coldgate
  - 2026-08-13-freeze-execution

## What deliberately stayed put, and why

These paths have named consumers. The full-path search was checked against tests, scripts, campaign files, and process records; the two qualifications below distinguish a path assembled in code from a literal match, and a historical citation from an active reader.

| Path | Why it stayed |
|---|---|
| `docs/stream_logs/` | `docs/process/state_kernel.json`, the live work-selection index, names a work log at its literal path. |
| `docs/reviews/` | `docs/process/state_kernel.json` names review reports and the comprehensive-audit register at their literal paths. |
| `docs/run_reports/` | `tests/test_build_site_parsers.py` reads the advisor-status-site report at its literal path; `scripts/build_site.py` extracts report paths from session entries. |
| `docs/advisor_briefs/` | `scripts/build_site.py` and `scripts/pack_capsule.py` read the window-A advisor brief at its literal path. |
| `docs/project_critique_review.html` | The full-path search found no literal match. `scripts/pack_capsule.py` does read this file, assembling the same path as `ROOT / "docs" / "project_critique_review.html"`. |
| `docs/project_status_history.md` | `tests/test_docs_freshness.py` reads this exact path and checks the status-history link. |
| `docs/JouleWise_Hardening_Proposal.md` | `tests/test_rpt002_related_work.py` reads the proposal and checks its literal path in source references. |
| `docs/axi-handoff.md` | `docs/process/state_kernel.json` names this exact path; `tests/test_gen_state.py` checks the reference. |
| `docs/strategy/2026-08-09-pack-freeze-plan.md` | `configs/campaigns/d117_floor_qwen25_1p5b_v1/plan_tree.json` preserves this literal source path in its campaign plan fixed before measurements. |
| `docs/process_traces/2026-07-15-axi-xhigh-consult/` | `docs/process/state_kernel.json` names the response at its literal path; `tests/test_gen_state.py` checks that reference. |
| `docs/process_traces/2026-07-17-floor-extraction/` | `scripts/build_site.py` reads the verified results file at its literal path. |
| `docs/process_traces/2026-07-24-diagnostic-extraction/` | `tests/test_floor_extraction.py` reads the measurement specification at its literal path. |
| `docs/process_traces/2026-08-03-q1-remint-bytecompare/` | `docs/process/state_kernel.json` retains this literal directory path in a status note about the completed comparison. |
| `docs/process_traces/2026-08-03-t3-doctrine-gate/` | `docs/process/state_kernel.json` names the synthesis at its literal path. |
| `docs/process_traces/2026-08-05-cgv-f3-consult/` | `docs/process/state_kernel.json` names the synthesis and consultation report at their literal paths. |
| `docs/process_traces/2026-08-07-plan-factory/` | `configs/campaigns/d117_contrast_v5/generate_configs.py` embeds the literal draft path in campaign material; `tests/test_d117_decode_contrast_plan.py` checks the reference. |
| `docs/process_traces/2026-08-08-attribution-debate/` | `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v2/analysis_manifest_v3.json`, a file listing the analysis plan fixed before measurements, names saved evidence at its literal path. |
| `docs/process_traces/2026-08-09-prefill-phase-proof/` | `tests/test_paper_terms_lint.py` reads the results file at its literal path. |
| `docs/process_traces/2026-08-14-readiness-charter-consult/` | The search found a literal citation in `docs/process/instrument-readiness-audit-charter.md`, which is marked superseded and retained as a record; it did not establish an active test, script, campaign file fixed before measurements, or live work-selection index that reads it. |

## A note on the largest files

Several archived transcripts are multiple megabytes because they contain the complete stdout (text output) of a past automated session, including its own echoed file diffs (before-and-after changes), saved verbatim. Their size records how much the session printed, not how important it was.
