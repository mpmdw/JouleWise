```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "partial",
  "summary": "Inventoried 3,881 documentation-surface files totaling 147.113 MB, including 3,809 files under docs/. Identified 596 audit-trail files totaling 86.894 MB, one retired compatibility pointer, and no confidently deletable redundancy. Literal dependencies, location-sensitive scans, immutable citations, and concurrent exclusions prevent blanket move clearance; the reference inventory below is static, not a proof of every runtime-resolved dependency.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "1d4045b4a6396f0e76e0128a827544bc1296edea",
    "head_end": "1d4045b4a6396f0e76e0128a827544bc1296edea",
    "upstream_end": "1d4045b4a6396f0e76e0128a827544bc1296edea",
    "branch": "chore/2026-09-10-docs-thin"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {"row": "Archive isolated advisor brief", "action": "start_now"},
      {"row": "Bulk historical moves", "action": "wait_for", "wait_for": "Owner-controlled reference and scan-boundary migration"},
      {"row": "Delete historical evidence or duplicate exhibits", "action": "do_not_start"},
      {"row": "Apply changes to excluded paths", "action": "do_not_start"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --porcelain",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["1d4045b4a6396f0e76e0128a827544bc1296edea"]},
      "expected": {"exit_code": 0, "tail_regex": "^1d4045b4a6396f0e76e0128a827544bc1296edea$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "Static reference discovery covers literal paths, joined Path expressions, documented globs and several manifest-driven consumers, but does not prove every runtime-resolved dependency.",
      "needs": "Treat bulk moves as conditional; verify affected consumers at the eventual move head."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "D-174 records explicit submission cuts and scope restrictions; under the requested precedence these cannot be dismissed using the general docs-are-context statement.",
      "needs": "Owner adjudication before treating those decision-log directives as retired."
    },
    {
      "id": "F3",
      "kind": "scope_deviation",
      "level": "nonblocking",
      "text": "An early static-path scanner called is_file on absolute source-code literals before filtering absolute paths, permitting metadata-only probes of canonical-checkout path literals. No canonical file contents were read and no files were modified.",
      "needs": "Recorded for lead review."
    }
  ]
}
```

## A. Class table

Sizes use **decimal MB**, calculated from file lengths, not allocated filesystem blocks. Counts include all files inside documentation directories, including their JSON, scripts, fonts and other supporting assets.

| Class | Files | MB | Rationale |
|---|---:|---:|---|
| **1 LIVE** | 3,284 | 60.217 | Current reader/tool dependencies; mixed operational directories conservatively retained. |
| **2 REDUNDANT** | 0 | 0 | No deletion candidate passed both content-equivalence and dependency checks. |
| **3 STALE DIRECTIVE** | 1 | 0.000804 | Explicitly retired planning-protocol compatibility pointer. |
| **4 AUDIT TRAIL** | 596 | 86.894 | Historical reports, deliberations, measurements, rulings and superseded campaign records; preserve bytes. |
| **Total** | **3,881** | **147.113** | Disjoint classification, including the trace partition below. |

**Observed `docs/`: 3,809 files, 145.709 MB.** `du -sk docs` reported 150,568 KiB allocated. This differs from the supplied 3,819-file/161-MB estimate; I used this worktree’s observed contents.

Class 4 is an **archival disposition, not immediate move clearance**. Several historical records are still cited or read by tests. Those are explicitly held below.

Scope outside `docs/`: root Markdown; complete `site_capsule/`, `env/`, `.agents/`, `.claude/`, `analysis/` and `figures/`; Markdown under `configs/` and `.github/`. Test fixtures were searched as **reference sources**, but were not classified as documentation to move. Runtime source trees and the standalone root mint artifact were not counted as documentation.

## B. Root Markdown table

| Path | Bytes | Class | Required justification / unique content |
|---|---:|---:|---|
| `AGENTS.md` | 6,637 | 1 **EXCLUDED** | Reader: repository agents. Repository safety, authority and handoff instructions. |
| `AGENT_PLAN.md` | 13,875 | 1 | Reader: implementing agent locating phase owners. Architecture, phase index, acceptance criteria and source-of-truth map; not merely status. |
| `CLAIMS_STATUS.md` | 15,912 | 1 | Reader: paper author checking whether a result may be quoted. Claim exclusions, registered limitations, evidence dispositions and “DO NOT QUOTE” history. |
| `CLAUDE.md` | 3,561 | 1 **EXCLUDED** | Reader: Claude lead. Tool-specific repository entry instructions. |
| `FREEZE-FCM01.md` | 3,796 | 4 | n/a. Round-4 terminal finding, exact-understatement mechanism, checked facts and freeze record. Preserve despite later FCM decisions. |
| `PROJECT_STATUS.md` | 12,756 | 1 | Reader: advisor Rivoire. Claim/scope explanation, measured evidence, gate matrix, advisor decisions and next milestone. |
| `README.md` | 17,513 | 1 | Reader: new user or contributor. Project introduction, operation/setup guidance and navigation. |
| `RUN_STATE.md` | 398,797 | 1 **EXCLUDED** | Reader: restarting magistrate. Generated restart view, stop card, handoff facts and extensive history. |
| `STATUS.md` | 1,496 | 4 | n/a. S14 stream handoff for the reviewed pinset-refresh lane, with branch/head-specific commands. Not project status; no conclusive whole-file superseder established. |
| `STOPPED-FCM01.md` | 2,027 | 4 | n/a. Round-5 stopping-rule execution and withdrawal rationale. Different finding from `FREEZE-FCM01.md`. |
| `TASK_QUEUE.md` | 718,517 | 1 **EXCLUDED** | Reader: magistrate selecting work. Generated task details, dependencies and completed-task history. |
| `WINDOW_STATUS.md` | 6,574 | 1 | Reader: operator checking the window annunciator; `scripts/window_status.sh` and its guard test. Contains operational interface plus stale `_v4` narrative. |

`CLAUDE.local.md` was absent in this worktree; its **EXCLUDED** designation still applies.

**The single operational status entry should be `RUN_STATE.md`.** This matches the explicit pointer in `PROJECT_STATUS.md`. Its editable work-selection source remains `docs/process/state_kernel.json`.

Making one file the authority for *all* status would conflict with **D-023** and **D-063**: exit checklists own phase completion; the kernel owns work selection; evidence owns claim validity. Preserve `PROJECT_STATUS.md` as the advisor summary, `CLAIMS_STATUS.md` as the claim-use register, `WINDOW_STATUS.md` as the operational annunciator, and `README.md` as the user entry point. Their unique content is listed above.

Two drift findings need owner attention:

- `CLAIMS_STATUS.md` still points at fresh `_v3` collection in its introductory banner; **D-164/D-167** establish `_v5`.
- `WINDOW_STATUS.md`’s August 24 `_v4` transaction narrative is superseded by **D-164/D-167**, but the file itself remains an operational interface.

## C. `docs/` directory table

“Last touch” is the directory’s latest Git commit date, not proof that every contained file remains current.

| Directory | Files | MB | Last touch | Class | Justification |
|---|---:|---:|---|---|---|
| `docs/advisor/` | 1 | 0.008 | 08-28 | 4 | Dated verification-sprint briefing; no external path or basename reference found. |
| `docs/advisor_briefs/` | 4 | 0.113 | 07-30 | 4 | Historical advisor communications. **Hold:** July 17 HTML is an active site/packager input. |
| `docs/campaign_packs/` | 11 | 0.164 | 09-04 | 1 | Reader: campaign preparer and `claims_lint.py`; contains preparation/preregistration material. |
| `docs/contracts/` | 30 | 0.992 | 09-10 | 1 | Readers: implementers, reviewers and contract tests. Soundness and custody contracts remain necessary. |
| `docs/design/` | 1 | 0.007 | 09-04 | 1 | Reader: maintainer of configuration-owned campaign declarations. D-174 parks follow-up work, not its implementation reference. |
| `docs/designs/` | 1 | 0.003 | 09-04 | 1 | Reader: cold-gate receipt maintainer. Documents durable publication behavior and its integration boundary. |
| `docs/evidence/` | 4 | 0.006 | 08-11 | 4 | Decisive-run evidence bundle. **Hold:** cited by ruling/history surfaces. |
| `docs/guides/` | 5 | 0.173 | 09-08 | 1 | Readers: new researcher, refusal reader and diagnostic-window operator. |
| `docs/paper/` | 94 | 5.735 | 09-08 | 1 **EXCLUDED** | Readers: paper authors, custody/replay/build tests. Mixed current and frozen material, all excluded. |
| `docs/phase_1/` | 3 | 0.041 | 09-04 | 1 | Reader: lead verifying external/hardware evidence and D-023 phase completion. |
| `docs/phase_2/` | 17 | 0.519 | 09-05 | 1 | Readers: window operator, instrument maintainer and tests. Contains historical subdocuments; unsafe to archive as a unit. |
| `docs/phase_3/` | 3 | 0.025 | 07-09 | 1 | Reader: lead checking recorded KV feasibility and phase evidence. Old date does not establish redundancy. |
| `docs/phase_4/` | 4 | 0.060 | 09-04 | 1 | Readers: claims linter, report builder and phase reviewer. |
| `docs/phase_5/` | 2 | 0.010 | 07-15 | 1 | Reader: submission reviewer locating final acceptance evidence; scheduling text needs reconciliation with D-174. |
| `docs/process/` | 26 | 0.763 | 09-10 | 1 **EXCLUDED** | Readers: magistrate, courier, watchdog and state generator. |
| `docs/process_traces/` | 3,205 | 101.958 | 09-10 | **Partition below** | A homogeneous classification would incorrectly archive executable dependencies or retain all history as live. |
| `docs/report_src/` | 19 | 0.050 | 09-04 | 1 | Readers: report builder and legacy-value exclusion tests. D-161’s addendum requires void outputs. |
| `docs/reviews/` | 76 | 1.334 | 07-19 | 4 | Historical critiques, adjudications and audit receipts. **Hold:** direct test reads and current citations. |
| `docs/run_reports/` | 106 | 1.349 | 09-04 | 4 | Dated session/evidence records. **Hold:** generated-site report resolution and many immutable citations. |
| `docs/site/` | 39 | 1.566 | 09-04 | 1 | Readers: Ed’s optional site workflow, packager and site tests. Generated output also contains independent assets and historical DRIFT records. |
| `docs/site_src/` | 4 | 0.040 | 09-04 | 1 | Reader: `scripts/build_site.py`; three HTML templates and CSS source. |
| `docs/specs/` | 27 | 0.749 | 09-04 | 1 | Readers: implementers and specification tests. Contains ratified designs and historical adjudications; not safely redundant with contracts. |
| `docs/strategy/` | 61 | 27.949 | 08-20 | 4 | Dated strategy/portfolio deliberations, freeze planning and recorded claims. **Hold:** generator, frozen-manifest and test references. |
| `docs/stream_logs/` | 47 | 0.385 | 07-17 | 4 | Historical per-stream decisions and evidence. Current documents still cite them. |

For the mixed directories retained as class 1, this is conservative **directory-level retention**, not a claim that every paragraph is current.

### Trace cutoff and exceptions

Recommended archival classification: **immediate trace directories dated before `2026-08-15`, except the six dependency-bearing directories below.**

| Partition | Files | MB | Class |
|---|---:|---:|---|
| All 51 immediate directories before cutoff | 299 | 74.322 | Subtotal, not a classification |
| Six retained directories below | 40 | 19.048 | 1 |
| Remaining 45 directories before cutoff | 259 | 55.275 | 4 |
| Six loose historical files directly in `process_traces/` | 6 | 0.069 | 4 |
| Directories dated August 15 onward | 2,900 | 27.566 | 1, conservative retention |
| **Disjoint trace totals** | **3,205** | **101.958** | **1: 2,940 / 46.615 MB; 4: 265 / 55.343 MB** |

| Retained old directory | Reader/dependency |
|---|---|
| `2026-07-15-axi-xhigh-consult/` | Kernel/AXI specification consumers; `test_gen_state.py` reads `response.md`. |
| `2026-07-17-floor-extraction/` | Site builder reads `extraction-verified.json`. |
| `2026-07-24-diagnostic-extraction/` | `test_floor_extraction.py` reads the A5 specification; refusal tutorial cites this evidence. |
| `2026-08-07-plan-factory/` | Renderer imports `lint_results_prose_template.py`; generators and frozen manifests reference the directory. |
| `2026-08-08-attribution-debate/` | Detection-floor code, extraction specifications and frozen campaign documents cite the common-mode evidence. |
| `2026-08-09-prefill-phase-proof/` | Paper terms test and paper/example sources consume `results.json`. |

The date cutoff is **not a safe automatic move command**. Of the 51 old directories, **46 have references from retained documents, code or configurations**, including historical passages inside current documents.

The additional **40 referenced class-4 directories** are:

| Referencing retained surface | Trace directories requiring citation preservation |
|---|---|
| `RUN_STATE.md`, `TASK_QUEUE.md` and/or their generated site views | `2026-07-13-bridge-v11`; `2026-07-16-axi-sb-live-probes`; `2026-07-17-axi-sc-live-probes`; `2026-08-03-calbracket-b1-gate`; `2026-08-03-q1-remint-bytecompare`; `2026-08-03-t3-doctrine-gate`; `2026-08-03-winB-reeval-stop`; `2026-08-04-calbracket-collision-consult`; `2026-08-04-calbracket-integration-collision`; `2026-08-04-incident-state-forgery`; `2026-08-04-quiet-guard-spec`; `2026-08-04-t3-char-pair`; `2026-08-05-cgv-f3-consult`; `2026-08-05-d079-issuance`; `2026-08-05-d113-rigor-consult`; `2026-08-05-t3-amend`; `2026-08-06-d079-issuance-coldgate`; `2026-08-06-d110-remint-fork`; `2026-08-07-d117-u-units`; `2026-08-07-u2-coldgate`; `2026-08-08-recovery-exits-escalation`; `2026-08-08-trust-scoping-escalation`; `2026-08-11-5c-readiness-contract`; `2026-08-11-fcm-coldgate`; `2026-08-11-staged-contracts`; `2026-08-12-evauth-coldgate`; `2026-08-12-mintvocab-coldgate`; `2026-08-13-freeze-execution` |
| Decision/council logs | `2026-07-14-c033-axi-consult`; `2026-07-16-device-list-brief`; `2026-08-03-d111-backfill`; `2026-08-07-prefill-feasibility`; `2026-08-12-calexits-mutation-consult`; `2026-08-14-readiness-charter-consult` |
| Site advisor brief | `2026-07-16-axi-sd-web-verification`; `2026-07-17-dspark-dflash-smoke` |
| `README.md` | `2026-07-17-exploratory-block` |
| Research-question registry/bank | `2026-07-17-extension-axes` |
| Paper fill registry / three-night freeze manifest | `2026-08-07-d117-plan-freeze` |
| `docs/phase_2/window_runbook.md` | `2026-08-08-d127-autonomous-loop` |

Only these five old directories had **no references in the retained-document/code/configuration scan**:

- `2026-08-06-qg-census-consult/`
- `2026-08-07-meta-sweeps/`
- `2026-08-07-night-hardening/`
- `2026-08-08-trust-fixture-substrate/`
- `2026-08-12-item1-margin-consult/`

They still have historical cross-references; preserve those before moving.

The six loose trace records classified 4 are `RESUME-2026-07-26.md`, `RESUME-2026-07-27.md`, `RESUME-2026-07-28.md`, `2026-07-13-bridge-v11.manifest.jsonl`, `2026-07-26-prereg-clock-mitigation.md`, and `2026-08-08-t1-consistency-sweep.md`. The RESUME banners explicitly retire them as restart pointers; their historical content remains protected.

Explicit trace exclusions, all retained:

| Path below `docs/process_traces/` | Files | MB |
|---|---:|---:|
| `2026-09-10-activation-96bfeca7/` | 200 | 2.574 |
| `2026-09-02-hands-free-week/` | 127 | 0.968 |
| `2026-09-09-rehearsal-harvest/` | 176 | 1.006 |

### Documentation outside `docs/`

| Surface | Files counted | MB | Class | Reader / justification |
|---|---:|---:|---:|---|
| `.agents/` | 1 | 0.003 | 1 | Top-level Codex consult workflow; bridge tests. |
| `.claude/` | 3 | 0.011 | 1 | Claude bridge launcher and delegation workflow; bridge tests. |
| `.github/` Markdown | 1 | 0.002 | 1 **EXCLUDED** | PR author and gate-ledger test. |
| `configs/` Markdown | 21 | 0.064 | 1 **EXCLUDED** | Campaign generators, pack validators and preregistration consumers. Preserve frozen README files. |
| `env/` | 4 | 0.008 | 1 | Environment/reproducibility operator and lockfile tests. Historical selection memo is mixed into this operational directory. |
| `site_capsule/` | 10 | 0.064 | 1 | Ed’s optional site workflow, capsule packager and tests. |
| `analysis/` | 18 | 0.044 | 4 | Historical report outputs and explicit void successors. **Hold:** manifest and regression-test dependencies. |
| `figures/` | 2 | 0.008 | 4 | Historical result figure and void replacement. **Hold:** report-slice tests and artifact manifests. |

## D. `docs/` loose-file table

| Path | Bytes | Class | Required justification |
|---|---:|---:|---|
| `docs/JouleWise_Hardening_Proposal.md` | 56,700 | 4 | n/a. Received proposal preserved with C-028 adjudication pointer; test/source-map pinned. |
| `docs/agent_playbook.md` | 24,054 | 1 | Reader: agent running Mission M0. Historical missions contain unique code-review pointers; extract only with preservation. |
| `docs/axi-handoff.md` | 14,277 | 4 | n/a. Dated Ed directive and override record; kernel and tests still reference it. |
| `docs/council_log.md` | 441,544 | 1 **EXCLUDED** | Reader: magistrate checking adjudications and process authority. |
| `docs/critique_text_extract.txt` | 23,063 | 4 | n/a. Earlier critique version; **not contained unchanged in the later HTML**. |
| `docs/decision_log.md` | 769,947 | 1 **EXCLUDED** | Reader: magistrate resolving authority and supersession; tests read it. |
| `docs/instrument-v2-lessons.md` | 64,132 | 4 | n/a. Explicit lessons/post-mortem memo, not a funded or scheduled commitment. |
| `docs/milestones.md` | 4,893 | 1 | Reader: Ed/lead recording authoritative external dates and sequence. |
| `docs/orchestration.md` | 29,583 | 1 | Reader: lead applying repository roles and review boundaries. |
| `docs/planning_reflection_protocol.md` | 804 | 3 | **Superseder: D-063**, explicitly named in its RETIRED banner; Mission M0/kernel own the procedure. **Test-pinned compatibility stub: hold.** |
| `docs/project_critique_review.html` | 45,907 | 4 | n/a. Critique plus later reassessment; capsule packager reads it. |
| `docs/project_status_history.md` | 6,073 | 4 | n/a. Explicit historical, non-operative ledger; freshness test reads it. |
| `docs/publication_release_checklist.md` | 7,418 | 1 | Reader: authorized release operator distinguishing smoke, controlled regeneration and publication. |
| `docs/research_question_bank.md` | 67,156 | 4 | n/a. Historical wording, rejected ideas, kills and deliberations. Registry is the live index, **not a full-content replacement**. |
| `docs/research_question_coverage-2026-08-28.md` | 55,643 | 4 | n/a. Dated coverage analysis; September 4 map changes the framing, not a verified replacement of every historical argument. |
| `docs/research_question_coverage-2026-09-04.md` | 16,076 | 1 | Reader: paper lead choosing current capstone scope against the live registry. |
| `docs/research_question_registry.md` | 41,076 | 1 | Readers: claims linter and research lead; canonical identifier/status/claim-ceiling index. |
| `docs/risk_register.md` | 26,044 | 1 | Reader: lead responding to risk triggers; site builder also reads it. |
| `docs/test_audit_2026-07-07.md` | 15,552 | 4 | n/a. Dated bug findings and verification results; preserve audit evidence. |

Additional self-declared stale material **inside retained directories**:

- `docs/phase_2/floor_workload_sizing.md`: RETIRED by **D-166**, September 4; retains a historical arithmetic boundary and is test-pinned.
- `docs/phase_2/window_c_operator_checklist.md`: SUPERSEDED by **D-117**; retains historical mechanics.
- `docs/strategy/2026-08-08-40h-plan.md`: explicit **D-133** supersession.
- `docs/strategy/2026-08-09-pack-freeze-plan.md`: explicitly rejects an earlier blanket supersession and requires item-level disposition. **Do not label the whole file disposable.**
- Readiness-council records: **D-167** retires the old gate but explicitly preserves charter/sitting records.

These remain within their directory classifications; they are not additional counted files.

## E. Top 30 largest documentation files

Prefix `T/` means `docs/process_traces/`; `S/` means `docs/strategy/`.

| # | Path | MB | Class |
|---:|---|---:|---:|
| 1 | `T/2026-08-07-plan-factory/DRAFT-QUANT_GATES.md` | 4.542 | 1* |
| 2 | `T/2026-08-07-meta-sweeps/CONSISTENCY-SWEEP.md` | 4.057 | 4 |
| 3 | `T/2026-08-07-plan-factory/DRAFT-REASONCODE.md` | 3.855 | 1* |
| 4 | `T/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md` | 3.571 | 4 |
| 5 | `T/2026-08-07-plan-factory/DRAFT-NEVERZERO.md` | 3.416 | 1* |
| 6 | `T/2026-08-07-meta-sweeps/PAPER-FORMAT.md` | 3.275 | 4 |
| 7 | `T/2026-08-07-meta-sweeps/DOCS-VS-PRACTICE.md` | 3.035 | 4 |
| 8 | `T/2026-08-07-d117-u-units/U3-DELTA-VERDICT.md` | 2.775 | 4 |
| 9 | `docs/paper/round7/prefill-resolvability-projection.json` | 2.414 | 1 **EXCLUDED** |
| 10 | `T/2026-08-07-night-hardening/AUDIT-MINT.md` | 2.366 | 4 |
| 11 | `T/2026-08-07-d117-u-units/U1-RECOVERY-FINALHEAD.md` | 2.298 | 4 |
| 12 | `T/2026-08-07-d117-u-units/U1-AUDIT-EXEC.md` | 2.291 | 4 |
| 13 | `T/2026-08-07-night-hardening/AUDIT-LEDGER.md` | 2.237 | 4 |
| 14 | `T/2026-08-07-plan-factory/DRAFT-U5U7.md` | 2.115 | 1* |
| 15 | `T/2026-08-07-d117-u-units/ESCALATION-CONSULT-RESPONSE.md` | 1.990 | 4 |
| 16 | `T/2026-08-07-meta-sweeps/CONTAMINATION.md` | 1.966 | 4 |
| 17 | `S/2026-08-07-paper-portfolio/proposals/prop-contamination-characterization.md` | 1.911 | 4 |
| 18 | `T/2026-08-07-night-hardening/AUDIT-PAPER-FIDELITY.md` | 1.852 | 4 |
| 19 | `T/2026-08-07-d117-u-units/U5-U7-PACK-SCOUT.md` | 1.851 | 4 |
| 20 | `T/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md` | 1.832 | 4 |
| 21 | `T/2026-08-07-d117-u-units/U1-DELTA2-VERDICT.md` | 1.808 | 4 |
| 22 | `T/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md` | 1.724 | 4 |
| 23 | `S/2026-08-07-paper-portfolio/proposals/prop-open-explore-registry.md` | 1.723 | 4 |
| 24 | `S/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md` | 1.690 | 4 |
| 25 | `S/2026-08-07-paper-portfolio/proposals/prop-long-generation-dynamics.md` | 1.682 | 4 |
| 26 | `T/2026-08-07-night-hardening/AUDIT-RUNNER.md` | 1.605 | 4 |
| 27 | `T/2026-08-07-plan-factory/DRAFT-U8.md` | 1.541 | 1* |
| 28 | `S/2026-08-07-paper-portfolio/proposals/prop-batch-concurrency-energy.md` | 1.464 | 4 |
| 29 | `T/2026-08-07-meta-sweeps/DECISION-COHERENCE.md` | 1.422 | 4 |
| 30 | `S/2026-08-07-paper-portfolio/proposals/prop-quantization-ladder.md` | 1.386 | 4 |

\* Class 1 follows the deliberately conservative **whole-directory retention** of `plan-factory/`. Its executable linter and frozen references prevent a directory move; this does not establish current operational value for every large transcript.

## F. TEST-PINNED list

**This is the primary move-safety output.**

Notation:

- **L**: literal or statically constructed path. Moving it without changing the consumer can break reads, writes, assertions or imports.
- **G**: glob/walk. It survives only if the moved item remains inside the selected root and still satisfies the selector.
- **C**: literal citation/comment/fixture text, not demonstrated executable file access. Preserve discoverability, but do not claim that the citation alone breaks execution.
- `t:name` expands to `tests/test_name.py`; `s:name` expands to `scripts/name.py`.
- Braces below enumerate fixed filenames; they are **not glob patterns**.
- Representative consumers are named; a path may have additional consumers.

### Root and loose-file pins

| Documentation path | Consumer | Kind |
|---|---|---|
| `AGENT_PLAN.md` | `t:docs_freshness`, `s:build_site` | L |
| `PROJECT_STATUS.md` | `t:docs_freshness`, `t:build_site_parsers`, `s:claims_lint`, `s:build_site` | L |
| `README.md` | `t:docs_freshness`, `s:claims_lint`, `s:build_site` | L |
| `RUN_STATE.md`, `TASK_QUEUE.md` | `t:gen_state`, `t:docs_freshness`, `t:build_site_parsers`, `s:gen_state`, `s:build_site` | L **EXCLUDED** |
| `AGENTS.md`, `CLAUDE.md` | `t:docs_freshness`, `t:bridge` | L **EXCLUDED** |
| `WINDOW_STATUS.md` | `tests/test_window_status_guard.py`, `scripts/window_status.sh` | L |
| `docs/JouleWise_Hardening_Proposal.md` | `t:rpt002_related_work`; also report source-map lookup | L |
| `docs/agent_playbook.md` | `t:docs_freshness` | L |
| `docs/axi-handoff.md` | `t:gen_state` | L |
| `docs/council_log.md` | `s:build_site`, `t:build_site_parsers` | L **EXCLUDED** |
| `docs/decision_log.md` | `s:gen_state`, `t:docs_freshness`, `t:identity_pins`, `t:capture_t0_step` and numerous contract tests | L **EXCLUDED** |
| `docs/orchestration.md` | `t:docs_freshness`, `s:build_site` | L |
| `docs/planning_reflection_protocol.md` | `t:docs_freshness` | L |
| `docs/project_status_history.md` | `t:docs_freshness` | L |
| `docs/project_critique_review.html` | `s:pack_capsule`, `t:pack_capsule` | L |
| `docs/research_question_registry.md` | `s:claims_lint` | L |
| `docs/risk_register.md`, `docs/milestones.md` | `s:build_site` | L |

A raw search for `STATUS.md` produced substring hits inside `PROJECT_STATUS.md` and `WINDOW_STATUS.md`. **Those are not pins on root `STATUS.md`.** No test/script dependency on the exact root `STATUS.md`, `FREEZE-FCM01.md` or `STOPPED-FCM01.md` was established.

### Contract, phase and specification pins

All entries in the first column below are relative to `docs/`.

| Paths | Consumer | Kind |
|---|---|---|
| `contracts/adapter_contracts.md` | `t:single_count_discipline_census`, `t:single_count_discipline_matrix`, `s:build_site` | L |
| `contracts/analysis_plans.md` | `t:modularity`, `t:analysis_manifest`, `s:claims_lint` | L |
| `contracts/bridge_protocol.md` | `t:bridge`, `t:docs_freshness`; `scripts/codex-bridge` citation | L/C |
| `contracts/calibration_ledger_append.md` | `t:calibration_exits` | L |
| `contracts/claims_ladder.md` | `s:claims_lint`, `s:build_site` | L |
| `contracts/d078_reason_registry_amendment.md` | `t:d078_reason_registry`, `t:arm_readiness_schemas` | L |
| `contracts/d117_step6_confirmation_table.md` | `t:family_marker` | L |
| `contracts/d165_dominance_closeout.md` | `t:d165_dominance_closeout` | L |
| `contracts/measurement_methodology.md` | `s:build_site`, `t:build_site_parsers` | L |
| `contracts/paper_comparison_placements.md` | `t:paper_comparison_placements` | L |
| `contracts/paper_reported_energy.md` | `t:paper_reported_energy`, `t:d117_floor_qwen25_1p5b_plan` | L |
| `contracts/paper_supply_custody.md` | `t:paper_custody`, `t:paper_comparison_placements`, `tests/fixtures/paper_custody/run_kills.py` | L |
| `contracts/powermetrics_fiducial.md` | `t:d078_reason_registry`; `s:validate_powermetrics_fiducial` | L/C |
| `contracts/quiet_guard.md` | `t:quiet_guard` | L |
| `contracts/receipt_histsem_verifier.md` | `t:receipt_histsem`, `t:gen_state` | L |
| `contracts/run_bundle_layout.md` | `t:d078_reason_registry` | L |
| `phase_2/{alpha,beta,gamma}_arm_readiness.md` | `t:arm_readiness_registry` | L |
| `phase_2/detection_floor.md` | `t:single_count_discipline_census`, `s:build_site` | L |
| `phase_2/floor_workload_sizing.md` | `t:workload_sizing` | L |
| `phase_2/phase_2_exit_checklist.md` | `t:docs_freshness` | L |
| `phase_2/window_runbook.md` | `t:calibration_exits`, `t:window_env_allowlist`, `t:check_window_provenance`, `s:gen_g2_phase_d`, `scripts/ed_session/build_rehearsal_env.sh` | L |
| `phase_4/claims_index.md` | `t:claims_index_lint`, `t:rpt001_report_slice`, `s:claims_lint` | L |
| `phase_4/related_work_draft.md` | `t:rpt002_related_work` | L |
| `specs/axi/sb_static_batch_verdict.md` | `t:gen_state` | L |
| `specs/c027/doc-008_state_kernel.md` | `t:docs_freshness`, `t:gen_state`, `s:gen_state` | L |
| `specs/c027/doc-009_repro-001_authority_and_repro.md` | `t:env_locks` | L |
| `specs/c027/p2-039_floor_artifact.md` | `t:detection_floor` introductory citation | C |
| `specs/c027/rpt-001_report_vertical_slice.md` | `t:rpt001_report_slice`; `s:make_figures` citation | L/C |
| `strategy/2026-08-09-pack-freeze-plan.md` | `t:d117_decode_contrast_plan` | C |
| `reviews/2026-07-13-comprehensive-audit/receipts/WO-030-clean-venv-smoke.json` | `t:env_locks` | L |
| `reviews/2026-07-13-comprehensive-audit/CHECKPOINT.md` | `tests/fixtures/state_kernel/historical_audit_gate.json` | C / fixture locator |
| `reviews/2026-07-19-measurement-soundness-audit.md` | `t:floor_extraction` split-line citation | C |
| `run_reports/2026-07-09-advisor-status-site.md` | `t:build_site_parsers` | Literal report pointer; preserve parser expectations |
| `advisor_briefs/2026-07-17-window-a-brief.html` | `s:build_site`, `s:pack_capsule` | L |

`tests/test_rpt001_report_slice.py` also explicitly asserts that **`docs/contracts/evidence_handoff.md` does not exist**. Do not recreate it as a relocation stub.

### Process and trace pins

Paths in this table beginning with a date are below `docs/process_traces/`.

| Path | Consumer | Kind |
|---|---|---|
| `docs/process/state_kernel.json` | `s:gen_state`, `t:gen_state`, `t:docs_freshness` | L **EXCLUDED** |
| `docs/process/state_kernel.schema.json` | `s:gen_state`, `t:gen_state` | L **EXCLUDED** |
| `docs/process/NIGHT_COURIER_PROMPT.md` | `s:run_night` | L **EXCLUDED** |
| `docs/process/NIGHT_HANDBACK.md` | `t:run_night`, `t:magistrate_watchdog` | L **EXCLUDED** |
| `docs/process/MAGISTRATE_WATCHDOG.md` | `t:magistrate_watchdog` | L **EXCLUDED** |
| `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md` | `s:magistrate_watchdog`, `t:magistrate_watchdog` | L **EXCLUDED** |
| `docs/process/rehearsal-operator-card.md` | `scripts/ed_session/build_rehearsal_env.sh` | L **EXCLUDED** |
| `docs/process/{coldgate_charter.md,coldgate_consult_brief_template.md,coldgate_charter_registry.md,coldgate_charter_v3_candidate.md}` | `t:coldgate_charter_v3` | L **EXCLUDED** |
| `2026-07-15-axi-xhigh-consult/response.md` | `t:gen_state` | L |
| `2026-07-17-floor-extraction/extraction-verified.json` | `s:build_site` | L |
| `2026-07-24-diagnostic-extraction/specs/a5_complete_supported_cells.json` | `t:floor_extraction` | L; adjacent Python string literals |
| `2026-08-07-plan-factory/lint_results_prose_template.py` | `s:render_results_fills`, `t:render_results_fills`, `t:results_prose_template` | **L import** |
| `2026-08-07-plan-factory/DRAFT-U5U7.md` | `t:d117_decode_contrast_plan` | C |
| `2026-08-08-attribution-debate/COMMONMODE-REPLAY.md` | `t:detection_floor` evidence-reference assertion | Literal basename |
| `2026-08-09-prefill-phase-proof/results.json` | `t:paper_terms_lint` | L |
| `2026-08-19-refreeze-execution/r6-issuance/prove_r6_neutrality.py` | `s:check_paper_replay_fence` citation | C |
| `2026-08-19-refreeze-execution/r6-issuance/r4-derivation.json` | `tests/fixtures/paper_first_use_pre_cure.md` | C / fixture locator |
| `2026-08-22-t20/real-transaction-runbook.md` | `t:midcampaign_cure_generation_docs` | L |
| `2026-08-22-t20/s0-runsheet-r4.md` | `t:s0_line_audit_guard`; `t:receipt_histsem` citation | L/C |
| `2026-08-27-t26/process-proposals/COLD-GATE-RULING.md` | `t:gen_state` | Literal authority reference |
| `2026-08-28-live-smoke/preflight.sh` | `t:preflight`, `t:check_window_provenance` | L |
| `2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md` | `s:gen_g2_phase_d`, `s:gen_derivation_night`, `t:gen_g2_phase_d`, `t:check_window_provenance` | L |
| `2026-08-28-workload-consult/04-MAGISTRATE-RULING.md` | `s:paper_prefill_resolvability_projection` | C |
| `2026-08-28-model-panel/`, `2026-08-30-prefill-margin-coldgate/` | `s:paper_prefill_resolvability_projection` | C directory references |
| `2026-08-30-prefill-margin-coldgate/03-MAGISTRATE-RATIFICATION.md` | `t:d117_contrast_v5_pack` | L |
| `2026-08-30-t28-estate11/estate-12-anchor-spec.json` | `s:derive_estate_anchors` | L |
| `2026-08-31-registry-v5/02-dg071-dg075-ratification.md` | `s:issue_dg071_dg075_statistics` | C |
| `2026-09-01-unattended/cold_start.json` | `t:run_night` | L |
| `2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md` | `t:docs_freshness` exemption set | Literal selector exception |
| `2026-09-02-coldgate-dx-t26a/MAGISTRATE-RULING-coldgate-dx-t26a.md` | `t:docs_freshness` | L |
| `2026-09-02-process-rules/MAGISTRATE-RULING-process-rules.md` | `t:docs_freshness` | L |
| `2026-09-02-decode-identity-set/22` | `t:identity_pins` abbreviated citation | C; incomplete filename |
| `2026-09-04-paper-custody/11-round-5-design-spec-astra.md` | `t:paper_custody` | L |
| `2026-09-04-peer-audit/43-magistrate-synthesis-gate-17.md` | `t:d117_contrast_v5_pack` | L |
| `2026-09-05-d166-prompt0/01-dependency-census.md` | `t:d117_contrast_v5_pack` | L |
| `2026-09-08-handoff-redo/78-coldgate-packet-d169-stage3/13-magistrate-synthesis.md` | `t:gen_state` | L |
| Same directory, `exhibit-A-consult-astra.md` | `t:gen_state` | Literal exhibit reference |

**Additional indirect pins:** freshness tests extract cited evidence paths from selected ruling bodies; site building resolves report paths from `RUN_STATE.md`; registry/manifest consumers resolve further paths from their inputs. Those dependencies cannot be reduced safely to the literal list alone.

### Paper pins — all EXCLUDED

Paths below are relative to `docs/paper/`.

| Paths | Consumer | Kind |
|---|---|---|
| `draft-v1.md` | `t:paper_build`, `t:paper_terms_lint`, `t:paper_renumber_refs`, `s:dependence_sensitivity`, `s:paper_renumber_refs` | L |
| `draft-v2-skeleton.md` | `t:paper_successor_migration`, `t:paper_first_use_ledger`, `t:paper_terms_lint`, `s:check_paper_replay_fence`, `s:check_paper_round7_artifacts` | L |
| `results-fill-registry.md` | `s:render_results_fills`, `s:check_paper_round7_artifacts`, paper comparison/terms tests | L |
| `protocol/prospective-comparison-protocol.md` | `t:paper_first_use_ledger`, `t:paper_terms_lint`, `t:paper_successor_migration` | L |
| `protocol/first-use-audit-ledger.md` | `t:paper_first_use_ledger`, `t:paper_successor_migration` | L |
| `round7/built-terms-lexicon.md` | `t:paper_first_use_ledger` | L |
| `round7/fill-checklist.md` | `t:paper_round7_artifacts`, `t:paper_successor_migration` | L |
| `round7/retensing-plan.md` | `t:paper_terms_lint`, `s:dependence_sensitivity` | L |
| `round7/dependence-sensitivity.md`, `round7/dependence-sensitivity.md.in` | `t:dependence_sensitivity`, `s:dependence_sensitivity` | L input/output |
| `round7/excursion-decomposition.json` | `t:paper_terms_lint`, `s:check_paper_round7_artifacts`, `s:paper_excursion_decomposition` | L |
| `round7/anchor-correction-quantified.json` | `s:check_paper_round7_artifacts`, `s:paper_anchor_correction_quantified` | L |
| `round7/prefill-resolvability-projection.json` | `s:paper_prefill_resolvability_projection` | Literal output |
| `round7/dg071-dg075-statistics.json` | `t:paper_terms_lint` | L |
| `round7/successor-migration-inventory.md` | `t:paper_successor_migration`; rationale allowlist fixture | L/C |
| `round7/structural-edits.md` | `tests/fixtures/d165_rationale_allowlist.json` | Literal allowlist |
| `round7/survival-map.md`, `artifact-guide.md` | `tests/fixtures/paper_first_use_pre_cure.md` | C / fixture locators |
| `fill-rehearsal/select_outcome_branches.py` | `t:select_outcome_branches`, `t:paper_successor_migration` | L import/execution |
| `fill-rehearsal/branch-selection.md`, `fill-rehearsal/rendered-refusal.md` | `t:paper_successor_migration` | L |
| `fill-rehearsal/dominance-reproduced-{alpha,beta}-{floor,extraction}.json` | `t:mint_floor_artifact`; alpha extraction also `t:single_count_discipline_matrix` | L, four files |
| `figures/reproduce_worked_examples.py`, `figures/build_mechanism_figures.py` | `t:paper_terms_lint` | L |
| `figures/worked-examples.json` | `t:paper_terms_lint` | L |
| `figures/figA_partial_record_enclosure.{json,svg}` | `t:paper_terms_lint` | L |
| `figures/{fig1_boundary_attribution.svg,fig3_decision_gates.svg,fig4_edge_excursions.svg,figA6_pulse_fit.svg}` | `t:paper_terms_lint`; figure 4 also round-7 artifact checker | L |
| `figures/{figA4_shared_signs.svg,figA5_clock_polygon.svg}` | `t:paper_terms_lint` SVG-name references | Literal filenames |
| `build/{build_paper.py,check_markdown.py}` | `t:paper_build` | L |

The D-165 allowlist fixture additionally names `docs/campaign_packs/d117_contrast_v5.md` and several contract/paper paths already listed.

### Report, site and outside-document pins

| Paths | Consumer | Kind |
|---|---|---|
| `docs/report_src/report.json` | `s:build_capstone`, `t:rpt001_report_slice`, `t:rpt002_related_work` | L |
| `docs/report_src/{references.csl.json,source_map.json}` | report profile; `t:rpt001_report_slice`, `t:rpt002_related_work` | L / manifest-resolved |
| All 10 `docs/report_src/chapters/` files and all 3 `appendices/` files | `s:build_capstone` via exact entries in `report.json` | **L through manifest**, not a free glob |
| `docs/report_src/generated/rpt001_vertical_slice.md` | `s:build_capstone`, `t:build_capstone`, `t:rpt001_report_slice` | L input/output |
| `docs/report_src/README.md` | `t:rpt001_report_slice` | L |
| `docs/report_src/report.md`, `chapters/07_results.md` | `t:claims_lint` | Literal paths |
| `docs/report_src/chapters/03_background_and_related_work.md` | `t:rpt002_related_work` | L |
| `docs/site_src/{index.html,research.html,results.html,site_sections.css}` | `s:build_site`, `t:build_site_parsers` | L |
| `docs/site/build_manifest.json` | `s:release_check`, `s:pack_capsule`, `s:build_site` | L |
| `docs/site/style.css`, `docs/site/fonts/fonts.css` | `s:build_site`, `s:pack_capsule` | L |
| Every font named by `docs/site/fonts/fonts.css` | `s:pack_capsule` CSS URL resolution | Indirect literal asset paths |
| `docs/site/DRIFT.md`, `docs/site/task_queue.html` | `t:docs_freshness` | L |
| Site HTML outputs including `readme`, `project_status`, `project_status_full`, `agent_plan`, `run_state`, `task_queue`, `risk_register`, `adapter_contracts`, `measurement_methodology`, `claims_ladder`, `orchestration`, `council_log`, `milestones`, `latest_run_report`, `advisor_brief`, `library`, `process`, `record`, `roadmap`, `status`, `decision_log` (`.html`) | `s:build_site`, `t:build_site_parsers`; several also `s:pack_capsule` | Literal output/route names; HTML walk also applies |
| `env/README.md`, `env/analysis-lock.txt`, `env/mac-measurement-lock.txt` | `t:env_locks`; lockfiles also quoted by paper fixture | L/C |
| `.github/pull_request_template.md` | `t:check_gate_ledger` | L **EXCLUDED** |
| `.agents/skills/claude-consult/SKILL.md` | `t:bridge` | L |
| `.claude/{agents/codex.md,commands/codex.md,skills/codex/SKILL.md}` | `t:bridge` | L |
| `site_capsule/{README.md,AGENTS.md,CLAUDE.md}` | `t:docs_freshness` | L |
| `site_capsule/server/index.ts`, `site_capsule/package.json` | `t:pack_capsule`, `s:pack_capsule` | Literal source/package paths |
| `configs/calibration/preregistration_d079_epoch_25g83_rev1.md` | `t:issue_calibration_acceptance_generation` | L **EXCLUDED** |
| `configs/campaigns/d117_floor_qwen25_1p5b_v{1,2,3}/README.md` | `t:d117_floor_qwen25_1p5b_plan` | L / generated-pack dependency **EXCLUDED** |
| `configs/campaigns/d117_floor_qwen25_7b_v{1,2,3}/README.md` | `t:d117_floor_qwen25_7b_plan` | L / generated-pack dependency **EXCLUDED** |
| `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v{1,2,3}/README.md` | `t:d117_decode_contrast_plan`; successor/v4 README exercised by `t:d117_gamma_d139a2_families` | L / generated-pack dependency **EXCLUDED** |
| `analysis/rpt001-v{1,2}/{aggregates.json,artifact_manifest.json,claims_index.jsonl,dataset.csv,input_manifest.json}` | `t:rpt001_report_slice`; claims indexes also `t:claims_index_lint`/`s:claims_lint`; v2 input manifest used by builders | L |
| `analysis/rpt001-v{1,2}/tables/{S1_legacy_stack_identity,T1_legacy_l1_results}.{md,csv}` | `t:rpt001_report_slice` | L |
| `figures/rpt001-v{1,2}/F1_legacy_l1_instrument_results.svg` | `t:rpt001_report_slice` | L |

### Glob/walk dependencies — moving does not necessarily preserve coverage

| Selected surface | Consumer | Move behavior |
|---|---|---|
| `docs/**/*.md`, excluding `docs/decision_log.md` and `docs/process_traces/**` | `tests/test_docs_freshness.py:286` | **G:** ordinary docs remain selected under `docs/legacy/`; moved traces become **newly included**. |
| `docs/process_traces/**/*MAGISTRATE-RULING*.md`, dated directory ≥ `2026-08-29` | Same test, `_dated_magistrate_rulings` | **G:** moving outside `process_traces/` removes coverage. |
| `docs/process_traces/**/*RULING*.md`, dated directory ≥ `2026-09-03`, excluding `NEEDS-RULING-*` | Same test | **G:** moving outside root changes coverage. |
| Cited evidence files inside selected ruling bodies | Same test, `_has_executed_evidence` | Content-derived paths; moving a cited target can break evidence checks. |
| `docs/site/*.html` | `t:docs_freshness`, `s:pack_capsule` | **G:** renames inside `site/` may remain selected; moving to legacy removes inputs. |
| `docs/campaign_packs/*.md` | `s:claims_lint` | **G:** moving out removes pack validation coverage. |
| `docs/report_src/**/*.{md,tex,typ}` | `s:claims_lint` | **G:** moving out removes claim-language coverage. |
| `analysis/**/*.md`, `figures/**/*.md`, limited to `tables`/`captions` ancestry | `s:claims_lint` | **G:** moving outside these roots removes coverage. |
| `docs/contracts/`, `docs/paper/`, `docs/campaign_packs/` | `t:d165_rationale_census` | Prefix-based census and path-specific allowlist; move changes coverage/allowlist matching. |
| `docs/paper/fill-rehearsal/**/*.py` | `t:single_count_discipline_census` | **G:** moving out removes supplier-code census coverage. |
| `.github/**` | `t:docs_freshness` | **G**, **EXCLUDED**. |
| `docs/slides`, `docs/captions`, `docs/tables`, plus root equivalents | `s:claims_lint` | Optional directory scans; directories were absent here. |
| Entire source snapshot | `s:release_check` | Git-tracked snapshot construction is broader than the explicit documentation literals. |

**Coverage limitation:** arbitrary runtime paths, environment overrides, manifest traversal and code imported by tests prevent a claim that grep alone has established every dependency. No tests were executed; some tests explicitly point at the prohibited canonical corpus, and others create scratch outputs.

## G. PROPOSED MOVE PLAN

No operations were executed.

Use the table as an ordered set of proposed `git mv SOURCE DESTINATION` operations. **Only row 1 is presently isolated enough for the later moving session to start directly.** Other rows wait for citation/consumer preservation and the appropriate owner-controlled changes.

| Order | Source → destination | Prerequisite |
|---:|---|---|
| 1 | `docs/advisor` → `docs/legacy/advisor` | No external full-path or basename reference found; retain file bytes. |
| 2 | `docs/process_traces/2026-08-07-meta-sweeps` → `docs/legacy/process_traces/2026-08-07-meta-sweeps` | Preserve historical cross-links; resolve freshness-scan boundary. |
| 3 | `docs/process_traces/2026-08-07-night-hardening` → `docs/legacy/process_traces/2026-08-07-night-hardening` | Same. |
| 4 | `docs/process_traces/2026-08-06-qg-census-consult` → `docs/legacy/process_traces/2026-08-06-qg-census-consult` | Same. |
| 5 | `docs/process_traces/2026-08-08-trust-fixture-substrate` → `docs/legacy/process_traces/2026-08-08-trust-fixture-substrate` | Same. |
| 6 | `docs/process_traces/2026-08-12-item1-margin-consult` → `docs/legacy/process_traces/2026-08-12-item1-margin-consult` | Same. |
| 7 | `docs/strategy` → `docs/legacy/strategy` | Frozen plan-tree/generator references and immutable citations must retain resolution. |
| 8 | `docs/stream_logs` → `docs/legacy/stream_logs` | Preserve decision-log, kernel and phase-checklist citations. |
| 9 | `docs/reviews` → `docs/legacy/reviews` | Preserve adjudication references and exact smoke-receipt test path. |
| 10 | `docs/run_reports` → `docs/legacy/run_reports` | Site report resolver and current/excluded documentation require owner migration. |
| 11 | `docs/advisor_briefs` → `docs/legacy/advisor_briefs` | Site builder/packager inputs require owner migration. |
| 12 | `docs/evidence` → `docs/legacy/evidence` | Preserve ruling/custody locators; no content edits. |
| 13 | `docs/critique_text_extract.txt` → `docs/legacy/critique_text_extract.txt` | Preserve historical citations. |
| 14 | `docs/instrument-v2-lessons.md` → `docs/legacy/instrument-v2-lessons.md` | Preserve its historical inbound citation. |
| 15 | `docs/research_question_coverage-2026-08-28.md` → `docs/legacy/research_question_coverage-2026-08-28.md` | Preserve historical citations. |
| 16 | `docs/test_audit_2026-07-07.md` → `docs/legacy/test_audit_2026-07-07.md` | Preserve critique/report citations. |
| 17 | `FREEZE-FCM01.md` → `docs/legacy/root/FREEZE-FCM01.md` | Preserve freeze-history citations; keep immutable. |
| 18 | `STOPPED-FCM01.md` → `docs/legacy/root/STOPPED-FCM01.md` | Preserve stopping-rule history. |
| 19 | `STATUS.md` → `docs/legacy/root/STATUS.md` | Preserve S14 handoff; do not execute its old commands. |

The remaining class-4 records are **second-stage archive candidates**, not included in this concrete batch. In particular, leave `analysis/`, `figures/`, test-pinned loose documents and the remaining referenced trace directories in place until their locators are addressed.

Do not content-edit historical files to repair links. The owner must select a relocation/compatibility mechanism that preserves old locators without rewriting records or silently changing validation coverage.

**Deletions: none.**

Evidence against tempting deletions:

- `critique_text_extract.txt` versus `project_critique_review.html`: normalized visible text was **19,049 versus 27,354 characters**, unequal and not whole-text containment. The HTML includes second-pass reassessment and changed claims.
- `site_capsule/AGENTS.md` and `CLAUDE.md`: `cmp` confirmed identity; MD5 both `726c7a1ee7512bd73cb5282ced13bc52`. They serve separate tool entry conventions and both are test-pinned.
- Fraunces 600/900 font files: byte-identical, MD5 `5d283517432688cbc312a7a954516cce`; both filenames are referenced by CSS.
- IBM Plex Sans 400/600: `cmp` confirmed identity; both filenames are referenced by CSS.
- Duplicate review exhibits and receipts were found by MD5 grouping. Their placement in separate evidence packets is itself part of the audit record; identity does not authorize deletion.

### Before/after estimates

These estimates exclude any later compatibility files or regenerated outputs.

| Scenario | Total files under `docs/` | Total MB | Files outside `docs/legacy/` | MB outside legacy |
|---|---:|---:|---:|---:|
| Before | 3,809 | 145.709 | 3,809 | 145.709 |
| Only isolated advisor move | 3,809 | 145.709 | 3,808 | 145.701 |
| Conditional rows 1–16 | 3,809 | 145.709 | 3,482 | 87.815 |
| Conditional rows 1–19, including three root records | 3,812 | 145.716 | 3,482 | 87.815 |

Rows 1–16 relocate **327 files / 57.894 MB**. The root moves add **3 files / 7,319 bytes** beneath `docs/`.

**Archiving inside `docs/` does not shrink total `docs/` storage.** It reduces the active browsing surface. No historical-data deletion is proposed.

## H. RISKS / DO-NOT-TOUCH

1. **Honor every explicit exclusion.** No move/delete recommendation applies to the excluded roots or three live trace directories. `docs/phase_2/derivation_night_runbook.md` was absent here; keep its exclusion rather than assuming the live checkout lacks it.

2. **Do not flatten evidence into “redundancy.”** Frozen plans, claim dispositions, failed measurements, pre-registrations, receipts, rulings and duplicate packet exhibits retain audit value independently of later summaries.

3. **Do not move `plan-factory/` as a unit.** It contains a Python module imported by the results renderer, plus frozen-plan references. Its 18.270 MB directory is a particularly misleading “old docs” candidate.

4. **A glob can fail silently.** Moving traces to legacy changes two opposing freshness scans: ruling checks lose inputs while the general Markdown decision-reference scan gains them. Passing tests after a move would not, by itself, prove preserved coverage.

5. **Frozen locators may be hash-bound.** Generator/plan-tree references, source maps, registry paths and historical custody locators need semantic inspection before any migration. A global search-and-replace is not acceptable.

6. **Single-status consolidation has an authority limit.** D-023/D-063 intentionally split phase evidence, work selection, restart projection and advisor summary. `RUN_STATE.md` can be the single operational entry point without deleting those distinct owners.

7. **Decision precedence exposes a real conflict.** D-174 contains explicit September acquisition/content-freeze cuts and parks several workstreams. Under this task’s precedence, the general September 1 “docs are context” statement does not automatically retire D-174. The inventory does not rule on restarting or dropping that work.

8. **D-161 is narrower than “remove operator guards.”** Its detailed entry distinguishes deliberate interference from operator mistakes; physics/evidence, preregistration and mistake protections remain. Its September 4 addendum expressly preserves the closed rpt001 publication route.

9. **Stale banners do not make entire records deletable.** FCM freeze/stopping records, old campaign readiness documents and strategy plans record different stages and mechanisms. D-133 and D-167 supersede operations while preserving historical evidence.

10. **No blanket REDUNDANT classification is supported for `docs/site/`.** It combines generated pages, static assets, manifests and independent historical DRIFT text. `site_src/` is a source dependency, not a duplicate build.

11. **Static reference completeness remains unproved.** Joined paths and several manifest consumers were inspected, but arbitrary runtime resolution was not exhaustively evaluated. That is why completion is marked partial and bulk moves remain conditional.

12. **Read-only execution caveat:** a heredoc was rejected because the shell attempted a temporary file; subsequent Python inspection used `-c`. An early AST scanner also performed metadata-only checks on absolute code literals before filtering them, as disclosed in the envelope. No repository files were changed; the worktree remained clean.

## I. PROPOSALS FOR EXCLUDED PATHS

These are **owner-only proposals**, not recommendations to apply them from this session.

| Excluded surface | Proposal for its owner |
|---|---|
| `RUN_STATE.md` | Keep it as the operational entry. In a separately authorized change, separate immutable historical checkpoints from the short current projection while preserving every historical byte and locator. |
| `TASK_QUEUE.md` | Keep generated live queue ownership with the kernel. Consider archiving completed historical tables without rewriting their records. |
| `docs/process/state_kernel.json` and other `docs/process/**` | When archive destinations are settled, migrate current pointers through the owner’s normal generation workflow. Do not hand-edit generated views. |
| `docs/decision_log.md`, `docs/council_log.md` | Preserve complete logs. Provide navigation/indexing or locator compatibility rather than rewriting old rulings to match new paths. |
| `scripts/**` | Inventory and update literal consumers together with any approved moves: especially `build_site.py`, `pack_capsule.py`, `claims_lint.py`, `render_results_fills.py`, and state/report generators. |
| `configs/**` | Preserve frozen README/spec/plan-tree references. If relocation requires changing a frozen locator, the owner must establish the permitted compatibility mechanism first. |
| `docs/paper/**`, `paper/**` | Keep current supply/custody/replay paths stable. Historical drafts and allowlists are not deletion candidates. |
| `.github/**` | Preserve CI/test coverage when moving files; do not make scans green by excluding the relocated evidence. |
| `AGENTS.md`, `CLAUDE.md`, `CLAUDE.local.md` | Eventually point intake at the compact operational entry and historical material at legacy navigation; preserve current authority during concurrent work. |
| Three explicitly live trace directories | No thinning proposal during the active run. Reconsider only after owner closure and a fresh dependency inventory. |
| `docs/phase_2/derivation_night_runbook.md` | Preserve its exclusion despite absence in this worktree; let the live owner reconcile it. |

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| Isolated advisor archive | start_now, in later moving session | Fresh clean-head check | `docs/advisor/` |
| Bulk archive batch | wait_for | Locator preservation and scan-boundary migration | Tests, scripts, frozen references, excluded documents |
| Single operational entry cleanup | wait_for | Owner-controlled changes | `RUN_STATE.md`, kernel, generated views |
| Evidence deletion | do_not_start | No deletion justified | Historical/custody records |

## Critical path

Bulk moves depend on preserving literal and immutable locators **and** test-selection semantics. Only after those dependencies are resolved should the owner apply the ordered moves and verify the affected consumers at the resulting head.

**CHECKS PERFORMED:** clean-tree/HEAD/upstream checks; filesystem file-count and byte-size inventories; `du -sk docs`; root/loose-file and directory inspection; `git log -1 --format=%ci -- <path>` for root files, loose docs, directories and selected traces; repository-wide supersession-marker scan; `rg` across both `tests/` and `scripts/`; joined-path/AST and manifest-consumer inspection; repository inbound-reference and basename searches; MD5 duplicate grouping; `cmp` on font and capsule-instruction pairs; normalized HTML/text critique comparison; no tests, network operations or file writes.