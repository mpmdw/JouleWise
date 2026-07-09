## WHAT I READ

- Core process documents: `agent_playbook.md`, `orchestration.md`, `planning_reflection_protocol.md`, `risk_register.md`, `RUN_STATE.md`, and `TASK_QUEUE.md`.
- Decision/council records: the decision index plus process- and sequencing-bearing entries D-023, D-031, D-041–D-043, and D-050; council index and detailed C-001/C-002/C-006–C-011/C-014–C-019/C-023–C-026 entries.
- Recent reports: meta-process cleanup, CP-5 resume, spec waves 1 and 2, and P2-034. Early comparison: the 2026-06-09 planning audit. Instrumentation anchors: checkpoint, resume/merge, and suite-build reports.
- Stream logs: DOC-007, CP-5/pre-campaign, P2-029 through P2-034.
- Both files under `docs/reviews/`.
- Read-only Git: status, log, show/stat, blame, process-document growth, relevant fix/bookkeeping commits, `scripts/codex-bridge`, and the local invocation manifest.

Bottom line: the individual catch stories are mostly credible—Git contains matching fixes—but the aggregate “catch rate/spend” instrument is not audit-grade. It has drifted toward persuasive retrospective narrative.

## FINDINGS

### BLOCKER

1. **RUN_STATE cannot currently yield one correct next action.** [RUN_STATE.md:91](/Users/edr/code/JouleWise/RUN_STATE.md:91) says the `[AGENT]` lane should take P2-022/P2-023, while simultaneously admitting their post-2M sequencing; binding D-041 explicitly keeps both post-2M [decision_log.md:2050](/Users/edr/code/JouleWise/docs/decision_log.md:2050). Later, RUN_STATE again names Wave-2 work as next [RUN_STATE.md:189](/Users/edr/code/JouleWise/RUN_STATE.md:189), although the queue marks every item DONE [TASK_QUEUE.md:95](/Users/edr/code/JouleWise/TASK_QUEUE.md:95). Git blame confirms the newer restart block was updated while the older “What Is Next” block was left intact. Failure scenario: a cold agent either redoes merged work or starts interop in violation of the winning decision log.

2. **The invocation evidence required to audit catch attribution does not exist for the sessions making the largest claims.** D-050 requires large delegated runs to leave an invocation map [decision_log.md:2495](/Users/edr/code/JouleWise/docs/decision_log.md:2495), and orchestration requires `parent_report`, role/lens, model, wrapper, disposition, and PR linkage [orchestration.md:169](/Users/edr/code/JouleWise/docs/orchestration.md:169). The bridge schema omits several of those fields and only appends a permanently pending disposition [codex-bridge:136](/Users/edr/code/JouleWise/scripts/codex-bridge:136). Local inspection found only two `/bin/echo` smoke rows—none for the later 20–46-agent sessions—and the recent reports provide no manifest pointer despite the template requiring one [run_reports/README.md:43](/Users/edr/code/JouleWise/docs/run_reports/README.md:43). Failure scenario: once scratch artifacts are pruned, “unique catch,” model attribution, session count, and token spend cannot be independently reconstructed.

### SHOULD-FIX

3. **Yield accounting mixes incompatible units and sometimes declares success by construction.** The Wave-2 “unique catches” block counts ten false findings killed by refuters alongside defects discovered [spec-fleshing-wave2.md:57](/Users/edr/code/JouleWise/docs/run_reports/2026-07-09-spec-fleshing-wave2.md:57). CP-5 says no layer produced zero catches [cp5-resume.md:159](/Users/edr/code/JouleWise/docs/run_reports/2026-07-09-cp5-resume.md:159), while RUN_STATE says both integration reviews were clean [RUN_STATE.md:172](/Users/edr/code/JouleWise/RUN_STATE.md:172). P2-034 reports “~5 sessions” while enumerating design, implementation, two lenses, fix, and final-head—six invocations [p2034-broad-packs.md:23](/Users/edr/code/JouleWise/docs/run_reports/2026-07-09-p2034-broad-packs.md:23). These are not evidence of fabricated fixes; they show the metric has no stable denominator or taxonomy. Failure scenario: a costly layer survives because clean verification or false-positive suppression is relabeled as a unique catch.

4. **The “drop after two zero-yield sessions” rule is both unenforced and demonstrably too crude.** The rule is explicit [orchestration.md:155](/Users/edr/code/JouleWise/docs/orchestration.md:155). Integration returned zero at C-017 [suite-build.md:121](/Users/edr/code/JouleWise/docs/run_reports/2026-07-08-suite-build.md:121), then both CP-5 integration waves were clean, which should have triggered deletion. Yet C-024’s next use caught five cross-stream seams [council_log.md:1363](/Users/edr/code/JouleWise/docs/council_log.md:1363). Failure scenario: mechanically following the rule deletes the layer immediately before a high-value catch; selectively ignoring it makes the “self-instrumenting” claim unfalsifiable.

5. **The intake and topology rules conflict, with D-031 clearly winning over stale playbook prose.** The playbook says one mission per session [agent_playbook.md:24](/Users/edr/code/JouleWise/docs/agent_playbook.md:24), whereas D-031 directs independent streams into separate worktrees [decision_log.md:1595](/Users/edr/code/JouleWise/docs/decision_log.md:1595), and orchestration treats decomposition as the normal substantial-session shape [orchestration.md:48](/Users/edr/code/JouleWise/docs/orchestration.md:48). Intake also varies: targeted RUN_STATE sections and conditional AGENT_PLAN reading in the playbook [agent_playbook.md:50](/Users/edr/code/JouleWise/docs/agent_playbook.md:50), versus full RUN_STATE/AGENT_PLAN/protocol intake [RUN_STATE.md:9](/Users/edr/code/JouleWise/RUN_STATE.md:9), versus mandatory latest-report intake in orchestration. Failure scenario: an agent can comply faithfully with one operating document while violating another.

6. **The pre-Window-A backup gate is not expressed consistently enough for a data-safety gate.** RUN_STATE makes P0-003 required before Window-A data accumulates while simultaneously naming quiet Window A as the top action [RUN_STATE.md:94](/Users/edr/code/JouleWise/RUN_STATE.md:94). The queue records the escalation [TASK_QUEUE.md:118](/Users/edr/code/JouleWise/TASK_QUEUE.md:118), but Mission M9 merely requires the already-completed interim protocol [agent_playbook.md:434](/Users/edr/code/JouleWise/docs/agent_playbook.md:434). R-016 confirms that protocol is same-disk and does not protect against disk failure [risk_register.md:291](/Users/edr/code/JouleWise/docs/risk_register.md:291). Failure scenario: a mission-driven agent starts floor/baseline collection believing M2 satisfies the gate, producing the first irreplaceable corpus on one disk.

7. **D-050’s mandatory revisit fired and was not adjudicated or back-annotated.** D-050 says to revisit after one complete stopped-and-resumed session [decision_log.md:2515](/Users/edr/code/JouleWise/docs/decision_log.md:2515); CP-5 completed exactly that cycle [cp5-resume.md:3](/Users/edr/code/JouleWise/docs/run_reports/2026-07-09-cp5-resume.md:3). D-043 requires fired clauses to be recorded, not silently left standing [decision_log.md:2137](/Users/edr/code/JouleWise/docs/decision_log.md:2137). Failure scenario: the manifest requirement remains nominally binding even though its first major trial exposed non-use and schema gaps.

8. **The one-fact-one-home architecture has regressed.** Orchestration calls RUN_STATE an intake pointer only [orchestration.md:140](/Users/edr/code/JouleWise/docs/orchestration.md:140), and C-009 reserves council bodies for genuine deliberation rather than session history [council_log.md:840](/Users/edr/code/JouleWise/docs/council_log.md:840). RUN_STATE now contains historical status, multiple prior verification blocks, session history, two next-action lists, and a cleared stop card. C-024–C-026 add pointer bodies that repeat their run reports [council_log.md:1357](/Users/edr/code/JouleWise/docs/council_log.md:1357). Since orchestration first landed, the five core process files grew from 3,106 to 4,893 lines; the wider process/history surface gained roughly 9,481 net lines in Git. Failure scenario: every close-out must reconcile several prose mirrors, producing exactly the stale restart split now present.

9. **The standalone planning-reflection protocol is presently ceremony, not an operative layer.** It mandates an eight-question audit for every substantial run [planning_reflection_protocol.md:18](/Users/edr/code/JouleWise/docs/planning_reflection_protocol.md:18) and a structured end reflection [planning_reflection_protocol.md:51](/Users/edr/code/JouleWise/docs/planning_reflection_protocol.md:51). None of CP-5, Wave 1, Wave 2, or P2-034 records those answers or credits the protocol with a unique catch; their process appendices start directly with pipeline shape, e.g. [spec-fleshing-wave1.md:46](/Users/edr/code/JouleWise/docs/run_reports/2026-07-09-spec-fleshing-wave1.md:46). By the project’s own two-session standard, the standalone ritual is a deletion/merge candidate. Failure scenario: agents spend intake budget reading a policy that the actual loop silently bypasses.

10. **Site close-out has two live policies.** RUN_STATE mandates regenerate and redeploy in the same session [RUN_STATE.md:44](/Users/edr/code/JouleWise/RUN_STATE.md:44), reinforced by orchestration [orchestration.md:96](/Users/edr/code/JouleWise/docs/orchestration.md:96). The latest report instead leaves redeployment to Ed “when convenient” [p2034-broad-packs.md:47](/Users/edr/code/JouleWise/docs/run_reports/2026-07-09-p2034-broad-packs.md:47). Failure scenario: the repository and generated static site move forward while the deployed advisor snapshot remains old; the fail-soft freshness overlay exposes drift but does not resolve the policy contradiction.

### NIT

11. **Literal state pointers are stale or mislabeled.** RUN_STATE calls `c095c83` “Main” [RUN_STATE.md:140](/Users/edr/code/JouleWise/RUN_STATE.md:140), while read-only Git shows current HEAD `529bffa`; this should say “last code-bearing verified head” if that is the intent. R-017 records the current repo as `~/code/CapstoneRivoire/Capstone` [risk_register.md:307](/Users/edr/code/JouleWise/docs/risk_register.md:307), while the actual workspace is `/Users/edr/code/JouleWise`. Failure scenario: cleanup/recovery instructions target an obsolete directory, or an agent falsely treats the recorded SHA as current.

## DESIGN JUDGMENT

The process has a valuable core, but its operating system should now be compacted. Keep the mechanisms with demonstrated differential yield:

- Lead live gates: C-006’s real-CLI resume defect and contamination true positive; C-017’s three live-only failures.
- Fresh counterreview and final-head review: repeatedly found blockers after green tests and prior review, including the PR #11 crash path.
- Integration review: real cross-stream catches in C-006, C-010, and C-024.
- Bounded design debate: C-014’s two lead-design reversals and C-023’s overturned attribution blocker.
- Consistency checking: it caught real drift, but the long-term solution is to remove duplicated state, not keep expanding the sweep.

I would move to this structure:

| Layer | Proposed home |
|---|---|
| Binding authority | Existing dated decision entries remain immutable. Add D-060 “Process Architecture v2” and dated addenda to D-023/D-031/D-043/D-050. Generate a short `docs/process/current_policy.md` containing only currently operative rules with decision IDs. |
| Live state | One machine-readable queue/state file containing task ID, lane, readiness, dependencies, authority, and acceptance. Generate both `RUN_STATE.md` and the current section of `TASK_QUEUE.md`; archive completed rows. |
| Session evidence | Per-session directory with `report.md`, `invocations.jsonl`, and `findings.jsonl`. Each finding gets a stable ID, severity, first detecting layer, duplicate-of links, disposition, and fix commit. “Unique catch” becomes a query, not prose judgment. |
| Historical narrative | Run reports own session history. Council log receives only genuine disputed positions and adjudications; stop adding pointer-only bodies. Decision/council indexes can be generated. |
| Agent procedure | One short preflight/close-out checklist. Mission playbooks contain mission mechanics only. Fold the useful planning fields—goal, fences, acceptance, evidence—into the task record and retire the standalone reflection document. |

Specific deletion/merge candidates under the project’s evidence rule:

- Retire `planning_reflection_protocol.md` as a standalone intake document; no unique catches are credited across the four recent sessions.
- Stop creating council pointer-body entries; C-024–C-026 add no information unavailable from their index row and run report.
- Remove cleared stop-card prose, prior verification history, and session history from live RUN_STATE. Preserve them in dated reports.
- Replace manual site regeneration/redeployment ritual with a CI/deployment job triggered by source changes.
- Do not delete integration review despite its two-zero run: that sequence proves the current deletion rule is unsound.

Replace the two-session rule with: evaluate after at least three *applicable* sessions, track accepted unique defects separately from false-positive suppression and clean verification, include lead minutes/token/wall-clock cost, and weight catches by severity and avoided loss. Safety and integration layers should be judged by expected-loss reduction, not raw hit frequency.

A clean cold-start should then report exactly:

- `[ED-EXTERNAL]`: resolve P0-003 before retaining Window-A evidence.
- `[QUIET-MAC]`: P2-015-SMOKE, then P2-015 floors, then P2-006—subject to the backup gate.
- `[AGENT]`: currently no unambiguously READY item. D-041 blocks P2-022/P2-023; P2-035 waits on floors; P2-028 lacks the bounded authority/artifact pointer demanded by the queue’s own READY rule. The correct action is to repair/clarify the queue, not infer permission.

## CHECKS PERFORMED

CHECKS PERFORMED: Static document review; read-only `git status`, `log`, `show`, `blame`, history growth, manifest/schema inspection, and claim-to-commit comparison. No suite or other tests run; no files changed. The worktree already contained unrelated modified/untracked user files and was left untouched.