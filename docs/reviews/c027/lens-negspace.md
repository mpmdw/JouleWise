## (a) WHAT I SKIMMED

I reviewed the requested orientation set: [README.md](/Users/edr/code/JouleWise/README.md), [PROJECT_STATUS.md](/Users/edr/code/JouleWise/PROJECT_STATUS.md), [AGENT_PLAN.md](/Users/edr/code/JouleWise/AGENT_PLAN.md), [TASK_QUEUE.md](/Users/edr/code/JouleWise/TASK_QUEUE.md), milestones, risk register, research-question registry, every phase plan/checklist, all campaign packs, and recent run reports through 2026-07-09. I also followed direct references into the capstone-scope and measurement-methodology contracts.

Several premises in the prompt need correction:

- The report and presentation are not absent. The plan assumes a final report and colloquium deck in Phase 5, and [PROJECT_STATUS.md](/Users/edr/code/JouleWise/PROJECT_STATUS.md:190) has a capstone artifact map.
- What the program actually grades is unknown. The repo assumes report + colloquium + repository/dataset, but the evaluator’s rubric, demo expectation, minimum figures, format, and deadlines are explicitly unresolved in [P1-008](/Users/edr/code/JouleWise/TASK_QUEUE.md:114).
- Data backup is not unplanned. R-016 has a script and restore test, but the destination is still on the same disk.
- Idle subtraction, measurement-overhead investigation, and cross-tool validation are not scientific blind spots. They have explicit policies or planned experiments. What is absent is executed calibration evidence and a few choices about the primary estimand.
- Aggregation infrastructure already exists in `joulewise/aggregate.py` with tests. The final figure/report pipeline does not.

## (b) TOP ABSENCES — RANKED BY EXPECTED REGRET

### 1. The actual grading contract and calendar

**Why missing:** Deliberate unresolved external dependency, not an unnoticed blind spot. Every phase target, supervisor meeting, borrow window, colloquium, and report deadline remains TBD in [milestones.md](/Users/edr/code/JouleWise/docs/milestones.md:3). P1-008 explicitly asks for the evaluator’s acceptance bar.

**Where it bites:** The project can optimize for an auditable benchmark while the program primarily grades a thesis document, a timed presentation, or a live demo. A late rubric discovery could invalidate the current priority order: for example, a required live demo has no owned deliverable, while developer-extension work does.

**Cheapest insurance:** Obtain one written program/advisor note covering due dates, report format/length, presentation duration, demo/poster requirement, minimum empirical result, and whether Mac-only plus analytical split inference passes. Then derive hard cut dates backward immediately.

### 2. A real report source and writing/revision runway

**Why missing:** The report is recognized but deliberately back-loaded. Phase 4 writes results and Phase 5.5 “assembles” them only after the dataset and figures freeze ([Phase 5 plan](/Users/edr/code/JouleWise/docs/phase_5/phase_5_plan.md:129)). There is no report source, institutional template, bibliography pipeline, page budget, chapter word budget, or advisor revision schedule.

**Where it bites:** “Assembly” turns out to include distilling hundreds of pages of plans into a coherent methods narrative, reconciling terminology, cutting scope, formatting citations, writing an introduction and conclusion, and absorbing supervisor feedback. The one-week claims-index margin in milestones is not a writing margin.

**Cheapest insurance:** Create the submission-format skeleton now and draft the stable introduction, problem statement, contribution statement, harness design, and methodology. Reserve at least two feedback cycles; treat Phase 5.5 as revision and finalization, not first integration.

### 3. An off-machine copy of the real corpus

**Why missing:** Explicitly user-deferred, not a blind spot. R-016 records a tested backup protocol, but `~/JouleWise-backup` is on the same disk; P0-003 is marked required before Window A ([risk register](/Users/edr/code/JouleWise/docs/risk_register.md:276), [queue](/Users/edr/code/JouleWise/TASK_QUEUE.md:119)).

**Where it bites:** Disk failure after a quiet Mac campaign or borrowed-hardware window destroys irreplaceable raw evidence. The six current real bundles and future campaign corpus are gitignored.

**Cheapest insurance:** Point the existing script at external/cloud storage and repeat the already-proven restore test. This is probably the highest-value five-minute operational action in the project.

### 4. A compound critical-path risk, including single-machine and human dependencies

**Why missing:** Risk-register blind spot. R-001, R-006, R-007, R-008, and R-012 cover individual failures, but not correlated slippage across advisor availability, NVIDIA/Orin access, wall-meter acquisition, network setup, the 3080 Ti window, the M3 Max, and the sole operator.

**Where it bites:** Hardware access arrives before the runbook is ready, or the runbook becomes ready after the loan window; the wall meter and CUDA machine are never simultaneously available; the Mac suffers an OS update or hardware problem during the only quiet campaign period. Each individual fallback looks safe, but their intersection leaves too little time even for the fallback study.

**Cheapest insurance:** Add hard evidence-by dates for every external gate and an automatic cut rule: if a gate is not proven by its date, the project moves permanently to the Mac + synthetic-transfer/analytical-composition floor. Book advisor and hardware windows before further optional expansion.

### 5. One end-to-end data-to-final-figure-to-report vertical slice

**Why missing:** Deliberate Phase 4 deferral, partly overtaken by implementation. Aggregation code exists, but `analysis/`, `figures/`, `scripts/make_figures.py`, the claims index, protocol-ratification note, and results draft are absent. The planned twelve-figure pipeline remains prose in [Phase 4](/Users/edr/code/JouleWise/docs/phase_4/phase_4_plan.md:102).

**Where it bites:** After the expensive corpus is frozen, the team discovers that required dimensions are awkward to aggregate, plot labels cannot express boundary differences cleanly, figure density exceeds the report page budget, or the intended claims cannot be supported by the exported table.

**Cheapest insurance:** Use the six existing bundles to produce one disposable but report-shaped F1/F2-style figure, one table, one claims-index row, and one embedded report page. This tests the complete consumer path without prematurely finalizing Phase 4.

### 6. Executed metrological validation—not merely its design

**Why missing:** Deliberate hardware-gated deferral. The project has unusually good designs for:

- gross and idle-subtracted reporting;
- idle-drift propagation;
- telemetry-on/off ABBA testing;
- wall/PD paired traces and bridge models;
- step, sustained, burst, and suite-shaped calibration loads.

Those appear in [detection_floor.md](/Users/edr/code/JouleWise/docs/phase_2/detection_floor.md:238) and the Q6 campaign pack. But P1-003 still has no meter decision, so there is no independent physical cross-validation of `powermetrics`, and true telemetry-on/off perturbation remains unknown.

**Where it bites:** A defense question such as “How do you know Apple’s modeled rail readings track workload energy?” can only be answered with boundary caveats and design intent. That is scientifically honest, but it caps the strength of absolute and cross-boundary claims.

**Cheapest insurance:** Decide immediately whether an external meter is available. If yes, run one small paired idle/step/sustained validation before broad campaigns. If not, freeze the limitation and stop spending effort on cross-boundary winner machinery.

### 7. A frozen counterfactual for “split saves energy”

**Why missing:** Scientific policy gap in a draft AP, rather than total conceptual neglect. The split pack calls both composite gross and composite idle-subtracted energy “primary” ([split campaign pack](/Users/edr/code/JouleWise/docs/campaign_packs/split_suite_q1_q2_q3.md:22)). It does not yet choose which system state is the actual decision counterfactual: two already-powered nodes, incremental workload energy, or total energy of provisioning the second node.

**Where it bites:** Split can appear favorable under idle-subtracted energy yet unfavorable when the second node’s standby cost is charged. Reporting both is good; allowing either to drive the headline after observing results creates a metric-selection vulnerability.

**Cheapest insurance:** Before split data, designate one primary estimand and service-state assumption. Make the other a named sensitivity analysis, including exactly how idle power and warm resident nodes are charged.

### 8. Between-session, between-day, and reboot reproducibility

**Why missing:** Registry blind spot. The project covers within-session ordering, drift sentinels, Window-B floor revalidation, version drift, second-unit replication, and cross-lab replication. It does not clearly own a small repeated-reference experiment across separated days/reboots as a source of session variance.

**Where it bites:** Tight within-session CIs look impressive, but measurements shift materially after reboot, ambient change, battery/charger state change, or OS daemon activity. The effect can be mistaken for workload/model differences if conditions are collected in separate sessions.

**Cheapest insurance:** Run one fixed reference cell at the start and end of every measurement day and after relevant reboot/software changes; preserve session ID as a blocking factor and report between-session variance separately.

### 9. Demonstrated third-party reproducibility with an exact runnable environment

**Why missing:** Partly implemented, deliberately unfinished. Bundles capture OS/runtime/model hashes and key MLX package versions; P2-027 provides pack/verify tooling. But there is no exact environment lock, published bundle pack, completed external re-reduction, or demonstrated fresh third-party setup. The installer constraints allow future versions rather than reconstructing the measured environment exactly.

**Where it bites:** A reviewer can inspect the evidence but cannot reproduce the analysis environment or execute the promised one-command re-reduction. Future dependency drift makes regeneration harder precisely when the report is being defended or archived.

**Cheapest insurance:** Freeze exact analysis and Mac environment versions, publish the existing small bundle pack, and have one uninvolved person perform the already-queued re-reduction. Hardware rerunning is unnecessary for this insurance.

### 10. The agent/review loop as a registered schedule and scope risk

**Why missing:** Risk-register blind spot despite substantial process documentation. Stop cards, councils, worktrees, counterreviews, and process traces address correctness, but there is no risk entry for the workflow optimizing its own machinery, spawning new research scope, or consuming calendar without advancing a grader-facing artifact.

**Where it bites:** Recent reports self-record roughly 2.5M tokens for spec wave 1, roughly 3M for wave 2, and about 600k for broad campaign packs; an advisor-facing site was also deployed and refreshed. Those efforts produced real quality improvements, but the project still has only six real corpus bundles, no Window-A floor/baseline corpus, no final figures, and no report source. The loop can remain productive locally while the capstone remains late globally.

**Cheapest insurance:** Register this as a risk with a simple trigger: if an agent-heavy work block produces neither a new real evidence bundle nor a report/figure increment, optional meta-process, site, registry, and campaign-pack work pauses. Limit concurrent future research questions until the core report artifact is green.

## (c) INVESTMENT JUDGMENT

The early rigor investment was justified. Raw-evidence retention, strict re-derivation, claims ceilings, detection floors, counterbalanced ordering, model/token provenance, and fail-closed campaigns directly protect the scientific deliverable. Several reviews caught defects that ordinary tests missed. Cutting that work retrospectively would be a mistake.

The marginal allocation has nevertheless tipped too far toward benchmark-platform completeness and meta-process sophistication. The clearest examples are:

- a deployed, live-refreshing advisor observatory before advisor scope and dates are captured;
- a 75-row research registry and packs for every pre-hardware-preparable question;
- external benchmark import, FLORES fertility, placement optimization, cross-lab replication, and developer-extension plans before the basic floor and homogeneous-baseline campaigns;
- a planned new tutorial adapter and extensive extension guide in Phase 5, although neither is obviously part of the grading rubric.

Those are credible research-infrastructure investments, but an undergraduate capstone normally receives credit through a bounded thesis argument supported by enough implementation and evidence—not through maximizing the number of future experiments the infrastructure could host. The broad packs are especially telling: many contain `PLANNED` commands and owners for infrastructure that does not yet exist, while the final plotting and report artifacts do not exist either.

The starved work is exactly what converts a strong repository into a gradable capstone:

- external clarification of the actual acceptance bar;
- off-machine corpus protection;
- quiet-window floor and baseline collection;
- one end-to-end analysis/figure/report slice;
- early report prose and advisor feedback;
- a demonstrated external re-reduction;
- hard calendar-based scope cuts.

My judgment is therefore: JouleWise is over-invested in proving that future science will be carefully governed and under-invested in producing the smallest finished scientific story a committee can read, see, and question. The right near-term stop line is not “no more rigor”; it is “no new breadth until the core evidence-to-report path exists.” The website, extra benchmark families, broad campaign packs, live split, extension tutorial, and further councils should all lose to dates, backup, Window A, one final-quality figure, and an actual report draft.

**CHECKS PERFORMED:** Read-only `rg`, `sed`, `find`, `ls`, file-existence, directory, and artifact-count inspections; no suite runs, hardware commands, network calls, or filesystem writes.