## What I read

Core documents:

- `README.md`
- `PROJECT_STATUS.md`
- `RUN_STATE.md`
- `TASK_QUEUE.md`
- `AGENT_PLAN.md`
- `docs/milestones.md`
- `CLAUDE.md`

Authority and evidence:

- `docs/decision_log.md`, especially D-004, D-014, D-016, D-023, and D-051–D-059.
- All five `docs/phase_N/phase_N_exit_checklist.md` files.
- `docs/phase_2/detection_floor.md`
- `docs/contracts/claims_ladder.md`
- `docs/contracts/token_normalization.md`
- Run reports for the first Mac measurements, 122B run, parallel-stream work, integrity/provenance merge, CP-5, spec waves 1/2, and P2-034.
- The six local real-run `summary_metrics.json` files.
- `.github/workflows/ci.yml` and relevant git history through `529bffa`.

## Findings

Reading only README plus PROJECT_STATUS gives the correct broad story—working Mac harness, genuine preliminary measurements, remote hardware still provisional, split study not yet executed—but not a fully accurate picture.

1. **BLOCKER — The headline per-token numbers use the wrong denominator label and mix gross with idle-subtracted metrics.** [`README.md:28`](/Users/edr/code/JouleWise/README.md:28), [`PROJECT_STATUS.md:94`](/Users/edr/code/JouleWise/PROJECT_STATUS.md:94), [`PROJECT_STATUS.md:231`](/Users/edr/code/JouleWise/PROJECT_STATUS.md:231), [`TASK_QUEUE.md:147`](/Users/edr/code/JouleWise/TASK_QUEUE.md:147). The advertised 77–88 mJ “per generated/output token” values are actually `energy_token_j`, whose denominator includes prompt plus output tokens. The bundles distinguish that from `energy_output_token_j`: for example 76.99 versus 79.40 mJ in rep 1 and 87.72 versus 90.46 mJ in rep 2 ([rep 1](/Users/edr/code/JouleWise/runs/example-mac-mlx-local__r1/summary_metrics.json:3), [rep 2](/Users/edr/code/JouleWise/runs/example-mac-mlx-local__r2/summary_metrics.json:3)). The prose also places ~47 J gross/request beside an idle-subtracted token value as if one derived from the other. **Fix shape:** in living docs, report gross and idle-subtracted request energy separately, then the correct idle-subtracted output-token range (~79.4–90.5 mJ); do the same for the 122B result. Add a corrective addendum to the immutable 2026-07-06 report rather than rewriting it.

2. **BLOCKER — The advisor-facing statistical decision rule is explicitly superseded and statistically wrong.** [`PROJECT_STATUS.md:327`](/Users/edr/code/JouleWise/PROJECT_STATUS.md:327) says differences are claimed only when marginal confidence intervals separate. D-053 says that rule is wrong for paired designs and requires the CI of the paired/block difference or named model contrast, never marginal-interval separation ([`decision_log.md:2602`](/Users/edr/code/JouleWise/docs/decision_log.md:2602)). **Fix shape:** replace the methodology bullet with the D-053 three-way contrast rule and detection-floor gate.

3. **BLOCKER — `RUN_STATE.md` gives two incompatible restart instructions, one of which asks agents to redo completed work.** The current restart section correctly points to Window A and post-Window-A work ([`RUN_STATE.md:91`](/Users/edr/code/JouleWise/RUN_STATE.md:91)), but “What Is Next” still lists P2-029 through P2-032 as the next wave ([`RUN_STATE.md:189`](/Users/edr/code/JouleWise/RUN_STATE.md:189)); all four are marked done in [`TASK_QUEUE.md:96`](/Users/edr/code/JouleWise/TASK_QUEUE.md:96) and are present in git history. **Fix shape:** delete the stale second ranking and retain one authoritative restart block that links to the queue.

4. **SHOULD-FIX — “Campaign-ready” outruns the actual gate state.** [`README.md:16`](/Users/edr/code/JouleWise/README.md:16) and [`PROJECT_STATUS.md:17`](/Users/edr/code/JouleWise/PROJECT_STATUS.md:17) call the instrument campaign-ready; the artifact map calls it “complete and campaign-ready” ([`PROJECT_STATUS.md:196`](/Users/edr/code/JouleWise/PROJECT_STATUS.md:196)). Yet Window A still requires P2-015-SMOKE and a production-shaped shakedown, while an external/cloud backup destination is mandatory before data accumulate ([`TASK_QUEUE.md:103`](/Users/edr/code/JouleWise/TASK_QUEUE.md:103), [`TASK_QUEUE.md:119`](/Users/edr/code/JouleWise/TASK_QUEUE.md:119)). This also directly contradicts “none of [the external input] blocks current work” at [`PROJECT_STATUS.md:252`](/Users/edr/code/JouleWise/PROJECT_STATUS.md:252). **Fix shape:** say “pre-campaign software review cleared; campaign execution remains gated on shakedown, calibration, quiet-machine availability, and external backup.”

5. **SHOULD-FIX — D-023’s declared status authority is not trustworthy because several exit-checklist rows are stale.** D-023 makes checklists the sole per-item authority ([`decision_log.md:1130`](/Users/edr/code/JouleWise/docs/decision_log.md:1130)), but Phase 3 marks the shipped KV-size helper pending ([`phase_3_exit_checklist.md:10`](/Users/edr/code/JouleWise/docs/phase_3/phase_3_exit_checklist.md:10)); Phase 4 marks the completed related-work draft pending ([`phase_4_exit_checklist.md:17`](/Users/edr/code/JouleWise/docs/phase_4/phase_4_exit_checklist.md:17)); and Phase 1 simultaneously calls Mac support partially checked and supported end-to-end ([`phase_1_exit_checklist.md:253`](/Users/edr/code/JouleWise/docs/phase_1/phase_1_exit_checklist.md:253), [`phase_1_exit_checklist.md:315`](/Users/edr/code/JouleWise/docs/phase_1/phase_1_exit_checklist.md:315)). **Fix shape:** reconcile the living checklist rows first, then derive coarse Phase 3/4 wording in AGENT_PLAN and PROJECT_STATUS from them.

6. **SHOULD-FIX — Current reader-facing result claims do not follow the project’s binding stack-identity contract.** D-058 makes the 11-field stack table binding on README/status prose ([`decision_log.md:2735`](/Users/edr/code/JouleWise/docs/decision_log.md:2735)); the contract requires every governed result to resolve to hardware unit, OS, runtime/version, model hash, tokenizer, output policy, batching, boundary, telemetry, and other fields ([`token_normalization.md:82`](/Users/edr/code/JouleWise/docs/contracts/token_normalization.md:82)). The exact numeric claims in README and PROJECT_STATUS name only a subset. **Fix shape:** add one compact named “measured stack” table and make each preliminary result resolve to it; keep request energy primary and token metrics explicitly tokenizer-scoped.

7. **SHOULD-FIX — The campaign-size figures conflict with D-054, so the named decision log must currently win.** D-054 records 170–340 bundles ([`decision_log.md:2649`](/Users/edr/code/JouleWise/docs/decision_log.md:2649)); the queue says 180–340 ([`TASK_QUEUE.md:95`](/Users/edr/code/JouleWise/TASK_QUEUE.md:95)). The detailed economics show why: 170 is the Window-A request/phase subset, while the minimum Window-B revalidation raises the total to 180 ([`detection_floor.md:154`](/Users/edr/code/JouleWise/docs/phase_2/detection_floor.md:154)). **Fix shape:** add a D-054 amendment distinguishing Window A from total campaign size, then align living docs. Preserve the dated run report unchanged.

8. **SHOULD-FIX — The milestone map still presents a completed authorization gate as awaiting rescheduling.** [`milestones.md:12`](/Users/edr/code/JouleWise/docs/milestones.md:12) says the Mac auth session is “to reschedule”; PROJECT_STATUS and the Phase 1 checklist record the privileged sample and sudo rule as complete on July 6 ([`PROJECT_STATUS.md:265`](/Users/edr/code/JouleWise/PROJECT_STATUS.md:265)). **Fix shape:** mark the constraint closed on 2026-07-06 and retain the missed June slot as a historical note.

9. **SHOULD-FIX — The advisor document understates the decision-log count and overstates its uniformity.** [`PROJECT_STATUS.md:227`](/Users/edr/code/JouleWise/PROJECT_STATUS.md:227) says 37 decisions, each with alternatives considered; the log contains D-001 through D-059, and several later entries record a promoted decision without an alternatives section. **Fix shape:** remove the volatile count or generate it; change “each with alternatives considered” to the narrower guarantee the log actually satisfies.

10. **SHOULD-FIX — Several absolutes are indefensible and readily quotable by a hostile reader.** “Displayed numbers can never diverge” ([`PROJECT_STATUS.md:215`](/Users/edr/code/JouleWise/PROJECT_STATUS.md:215)) is not guaranteed merely by sharing a read layer. “Every claim auditable” ([`PROJECT_STATUS.md:550`](/Users/edr/code/JouleWise/PROJECT_STATUS.md:550)) sits beside a still-planned claims index and a pending external re-reduction demonstration. **Fix shape:** use testable wording: the shared layer reduces drift and current bundles support internal re-derivation; external reproducibility and the full claims index remain pending.

11. **SHOULD-FIX — `PROJECT_STATUS.md` is an accreted status archive, not a 30-second standalone advisor view.** Before the actual summary, readers encounter one site-focused update, three “Previous Update” sections, and a ledger ([`PROJECT_STATUS.md:28`](/Users/edr/code/JouleWise/PROJECT_STATUS.md:28)); a 130-line orchestration essay follows the project content ([`PROJECT_STATUS.md:493`](/Users/edr/code/JouleWise/PROJECT_STATUS.md:493)). The latest “This Update” foregrounds the status website rather than the July 9 scientific and campaign work. **Fix shape:** keep only current status, current gates, artifact state, risks, and next milestone; move prior updates verbatim to a status-history document and rely on immutable run reports for detail; replace the process essay with a short link to `docs/orchestration.md`.

12. **NIT — The architecture diagrams still list Hailo as conditionally viable after the binding unsupported verdict.** [`AGENT_PLAN.md:62`](/Users/edr/code/JouleWise/AGENT_PLAN.md:62) and [`PROJECT_STATUS.md:275`](/Users/edr/code/JouleWise/PROJECT_STATUS.md:275) say `hailo-if-viable`, while the same status document’s target table says unsupported. **Fix shape:** label it `hailo — unsupported_workload; feasibility finding only` or remove it from the runtime-adapter path.

## Design judgment

The conceptual separation is good: README for entry, PROJECT_STATUS for advisors, RUN_STATE for handoff, TASK_QUEUE for work selection, AGENT_PLAN for the phase index, and exit checklists for evidence. The problem is that each document has gradually acquired parts of the others.

I would:

- Keep README and PROJECT_STATUS separate; they serve different readers.
- Reduce PROJECT_STATUS to roughly two pages: current claim, measured evidence, gate matrix, advisor asks, next milestone, and evidence links.
- Move all “Previous Update” prose to a status-history archive without altering dated run reports.
- Remove the Process Note from PROJECT_STATUS; `docs/orchestration.md` already owns it.
- Collapse RUN_STATE’s two next-step sections into one; let TASK_QUEUE own ordering.
- Move completed queue rows to a completed-task ledger, retaining only a short “recently closed” block in the live queue.
- Keep AGENT_PLAN mostly timeless. If coarse checkboxes remain under D-023, either generate them from checklists or accept that manual mirrors require a mandatory reconciliation step.

The cost is extra clicks for historical narrative and less immediate visibility into the orchestration story. The benefit is much larger: an advisor sees the scientific state before process history, while agents have only one actionable next-step surface. Given the demonstrated same-day drift, that trade is worthwhile.

## Checks performed

Static-only: inspected git status/log/diffs, CI triggers, all required docs and phase checklists, relevant D-entries and run reports, six real bundle summaries, bundle count, test-count provenance, adapter/tool presence, dates, gate states, and current-path evidence; no tests, hardware commands, or network access were run.