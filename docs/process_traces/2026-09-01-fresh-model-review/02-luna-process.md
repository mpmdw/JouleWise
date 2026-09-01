```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The repository is conditionally paper-ready, but its authoritative work selector is stale and process overhead now exceeds its safe marginal value.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "3b3839c0636bfb5e6fe5537178b1929551dac139",
    "head_end": "1d4b4ba47b98cca1782990fa7843a62948a4ed59",
    "upstream_end": "1d4b4ba47b98cca1782990fa7843a62948a4ed59",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [
    "docs/process_traces/2026-09-01-fresh-model-review/"
  ],
  "verdict": {
    "findings": [
      {"id": "F1", "severity": "blocker", "title": "Stale authoritative work selector"},
      {"id": "F2", "severity": "should_fix", "title": "T26 ruled-not-installed count lacks current-head closure"},
      {"id": "F3", "severity": "should_fix", "title": "Review gauntlet is not consistently risk-proportional"},
      {"id": "F4", "severity": "should_fix", "title": "Review provenance and release-proof custody remain incomplete"},
      {"id": "F5", "severity": "nit", "title": "Newcomer path and historical document structure are too large"},
      {"id": "F6", "severity": "nit", "title": "Several process checks and status documents are stale"},
      {"id": "F7", "severity": "nit", "title": "Further generic orchestration layers are not worth adding"}
    ],
    "overall": "Conditional yes: the measurement and evidence doctrine can support a defensible capstone, but only after the current campaign pointer is reconciled.",
    "single_biggest_change": "Reconcile the state kernel, generated queue, and RUN_STATE around the actual Qwen3 _v5 G2-a action.",
    "single_biggest_protection": "Keep fail-closed rules for physics, evidence integrity, pre-registration, and immutable raw evidence."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## main...origin/main"]},
      "expected": {"exit_code": 0, "tail_regex": "^## main\\.\\.\\.origin/main$"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 scripts/gen_state.py --check; rc=$?; printf 'exit=%s\\n' \"$rc\"; exit \"$rc\"",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["exit=0"]},
      "expected": {"exit_code": 0, "tail_regex": "^exit=0$"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 2791 tests in 119.937s", "FAILED (errors=1787, skipped=112)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "FAILED \\(errors=1787, skipped=112\\)$"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "HEAD advanced from 3b3839c0 to 1d4b4ba4 during this read-only review through concurrent review-trace bookkeeping commits.",
      "needs": "Use 1d4b4ba4 as the final review baseline and recheck state-sensitive findings after further commits."
    },
    {
      "id": "G2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "RUN_STATE names Qwen3 _v5 G2-a as next, while the authoritative kernel still blocks all quiet work and exposes the old Qwen2.5 D117 task.",
      "needs": "Reconcile the campaign pointer before G2-a."
    },
    {
      "id": "G3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The canonical suite could not run normally because this sandbox has no usable temporary directory; most failures are tempfile-related, with additional argument/parser failures.",
      "needs": "Run the suite in the normal writable CI environment before using it as evidence."
    }
  ]
}
```

## Findings

### VERDICT

Conditional yes: the repository can produce a defensible capstone paper in the next ~10 days because the `_v5` campaign inputs and result-fill path are frozen and explicitly pending data ([README.md:43](/Users/edr/code/JouleWise/README.md:43), [README.md:59](/Users/edr/code/JouleWise/README.md:59)). The immediate danger is operational: T29 says Qwen3 G2-a is next ([RUN_STATE.md:13](/Users/edr/code/JouleWise/RUN_STATE.md:13), [RUN_STATE.md:25](/Users/edr/code/JouleWise/RUN_STATE.md:25)), while the authoritative kernel still says no quiet task is allowed and names the old Qwen2.5 task ([RUN_STATE.md:5045](/Users/edr/code/JouleWise/RUN_STATE.md:5045), [RUN_STATE.md:5064](/Users/edr/code/JouleWise/RUN_STATE.md:5064)). That is fail-closed enough to stop a silent wrong run, but unclear enough to cause delay or invite a manual bypass. I would reconcile that selector before G2-a and protect the fail-closed physics, evidence, and pre-registration rules retained by D-161 ([docs/decision_log.md:188](/Users/edr/code/JouleWise/docs/decision_log.md:188)).

### WOULD CHANGE

1. **F1 — Change now (pre-campaign): reconcile the live work selector.**

   Observation: the queue declares the state kernel the sole source of truth ([TASK_QUEUE.md:562](/Users/edr/code/JouleWise/TASK_QUEUE.md:562)), but the kernel is marked updated on August 28 ([docs/process/state_kernel.json:4999](/Users/edr/code/JouleWise/docs/process/state_kernel.json:4999)) and still authoritatively blocks quiet work ([docs/process/state_kernel.json:4](/Users/edr/code/JouleWise/docs/process/state_kernel.json:4), [docs/process/state_kernel.json:21](/Users/edr/code/JouleWise/docs/process/state_kernel.json:21)).

   Why it matters: the next physical action, pack identity, and clearance condition are not represented in the control plane that agents are instructed to obey.

   First step, within one day: add an explicit `_v5` G2-a row or time-bounded exception to the kernel, regenerate both projections, and check that the campaign ID, pack digest, research-question registry, next action, and gate agree.

   Cost/risk: roughly half a day and a possible accidental gate-clearing mistake; require one independent review of the resulting state.

2. **F2 — Change now (pre-campaign): turn the T26 census into a current-head closure map.**

   Observation: the T26 sweep found 460 implementation clauses, including 53 not installed, 69 installed without a check at the point where bytes are made, and 122 not enforced there ([FINDINGS-TABLE.md:3](/Users/edr/code/JouleWise/docs/process_traces/2026-08-27-t26/ruled-not-installed-sweep/FINDINGS-TABLE.md:3), [FINDINGS-TABLE.md:9](/Users/edr/code/JouleWise/docs/process_traces/2026-08-27-t26/ruled-not-installed-sweep/FINDINGS-TABLE.md:13), [FINDINGS-TABLE.md:17](/Users/edr/code/JouleWise/docs/process_traces/2026-08-27-t26/ruled-not-installed-sweep/FINDINGS-TABLE.md:17)). This is a clause count, not a normalized count of distinct rulings, and its baseline predates later W-10 work ([RUN_STATE.md:41](/Users/edr/code/JouleWise/RUN_STATE.md:41)).

   Why it matters: “ruled” has repeatedly failed to mean “installed,” and the failure can survive a green clone proof until claim consumption.

   First step: audit only transaction-relevant `_v5` clauses across generator, freeze/readiness, collector, finalizer, and claim edge; mark each cured, superseded, or open, and require a producer-side refusal test for every remaining load-bearing rule.

   Cost/risk: this may reopen old architectural questions, so do not attempt to close all 460 clauses before the campaign.

3. **F3 — Change now (pre-campaign): freeze the review shape and tier it by consequence.**

   The process doctrine is substantial: two or three counterreview lenses, fixes, test amplification, a writer-versus-reviewer test audit, final-head review, integration review, and live gates ([docs/orchestration.md:64](/Users/edr/code/JouleWise/docs/orchestration.md:64), [docs/orchestration.md:85](/Users/edr/code/JouleWise/docs/orchestration.md:85)). My first-parent audit found 711 commits since August 1. Using a deliberately broad bucket—`joulewise/`, executable scripts, configs, and paper text—146 commits touched code/config/paper, while 559 touched the process-document set defined by the artifact table ([docs/orchestration.md:146](/Users/edr/code/JouleWise/docs/orchestration.md:146)); overlap is allowed, so this is not a pie chart, but process churn is clearly dominant.

   This is not merely documentation theater. Two cases clearly paid for themselves:

   - The C-058 arm-author delta caught a time-of-check/time-of-use stale census and a missing runbook producer ([docs/council_log.md:3573](/Users/edr/code/JouleWise/docs/council_log.md:3573), [docs/council_log.md:3587](/Users/edr/code/JouleWise/docs/council_log.md:3587)).
   - The T28 contract and delta reviews caught defects invisible to implementer test matrices, including a one-pin bypass, a vacuous oracle, hand transcription hidden behind a facade, and forged line indexing; the cold refuter also found six unnamed implementation sites ([docs/council_log.md:3863](/Users/edr/code/JouleWise/docs/council_log.md:3863), [docs/council_log.md:3869](/Users/edr/code/JouleWise/docs/council_log.md:3869), [docs/council_log.md:3883](/Users/edr/code/JouleWise/docs/council_log.md:3883)).

   Two cases clearly did not:

   - The C-039 pending-refuter layer produced no report because its background job died, leaving a zero-catch layer ([docs/council_log.md:2209](/Users/edr/code/JouleWise/docs/council_log.md:2209), [docs/council_log.md:2215](/Users/edr/code/JouleWise/docs/council_log.md:2215)).
   - In C-058, five relay agents spent roughly seven hours wedged before five ordinary relaunches completed in thirteen minutes ([docs/council_log.md:3651](/Users/edr/code/JouleWise/docs/council_log.md:3651)).

   First step: classify remaining work into physics/claim/pre-registration, ordinary code, and documentation/bookkeeping. Use the full chain only for the first category, targeted review and tests for the second, and one light review for the third.

   Cost/risk: this sacrifices some chance of discovering a rare cross-stream defect, but preserves the high-yield delta, integration, live, and final claim gates.

   Minimum process for the next ten days:

   - One authoritative campaign card or kernel entry with pack digest, registered questions, next action, owner, and gate.
   - Frozen pre-registration, immutable raw evidence, and no post-hoc sample or claim selection.
   - Physics/evidence refusal at the producer and claim edge.
   - Full independent review only for changes affecting those boundaries.
   - One immutable run receipt and lead sign-off before paper values are filled.

4. **F4 — Change now for the campaign; finish the release check after it closes.**

   Observation: the bridge contract admits that final snapshots cannot detect modified-then-restored files, ignored-file history, or writes outside the repository ([bridge_protocol.md:632](/Users/edr/code/JouleWise/docs/contracts/bridge_protocol.md:632), [bridge_protocol.md:635](/Users/edr/code/JouleWise/docs/contracts/bridge_protocol.md:635)). C-058 records six review reports without manifests and `.status` files saying `OK` beside `ACCEPTANCE_FAILED` ([docs/council_log.md:3756](/Users/edr/code/JouleWise/docs/council_log.md:3756), [docs/council_log.md:3762](/Users/edr/code/JouleWise/docs/council_log.md:3762), [docs/council_log.md:3767](/Users/edr/code/JouleWise/docs/council_log.md:3767)). The T26 sweep also lost per-clause custody for three seats because the authorized report writes were blocked ([FINDINGS-TABLE.md:93](/Users/edr/code/JouleWise/docs/process_traces/2026-08-27-t26/ruled-not-installed-sweep/FINDINGS-TABLE.md:93), [FINDINGS-TABLE.md:104](/Users/edr/code/JouleWise/docs/process_traces/2026-08-27-t26/ruled-not-installed-sweep/FINDINGS-TABLE.md:104)).

   Why it matters: process claims are not automatically evidence of paper reproducibility.

   First step: for G2-a, require one immutable manifest containing the exact head, pack digest, raw-root digest, command, verdict, and producer checks. After the campaign, add a release check for missing manifests and contradictory status files. The production-proof workflow is currently manual-only because of fixture drift ([d117-production-proof.yml:3](/Users/edr/code/JouleWise/.github/workflows/d117-production-proof.yml:3), [d117-production-proof.yml:12](/Users/edr/code/JouleWise/.github/workflows/d117-production-proof.yml:12)).

   Cost/risk: more ceremony around each run, but much less than discovering after collection that the audit trail cannot be reconstructed.

5. **F5 — Change after the campaign closes: give newcomers a small reader path and archive history safely.**

   The decision log is 10,403 lines and 664,941 bytes. Its index has 166 unique IDs and the body has 166 unique IDs, so ID-level parity is good ([docs/decision_log.md:22](/Users/edr/code/JouleWise/docs/decision_log.md:22)). However, there are 172 primary-heading matches because several IDs have duplicate headings. A title scan finds 22 amendment rows and 13 supersession rows, with three overlapping; the index has no normalized amendment/supersession field.

   The council log is 3,895 lines and 437,615 bytes, with 48 headings but 44 unique council IDs. Its own header says the record should be concise ([docs/council_log.md:3](/Users/edr/code/JouleWise/docs/council_log.md:3)). The process-trace tree is 99 directories, 1,319 files, and about 99 MB. A bounded external-reference scan found all 99 directories referenced somewhere else, so none is safely deletable as an orphan.

   A newcomer needs: `README.md`; the current T29 and generated sections of `RUN_STATE.md`; the current campaign and fill registry; D-161 through D-166; the relevant evidence contract; and only the M0, risk-tier, council, and spend sections of the playbook and orchestration guide ([README.md:253](/Users/edr/code/JouleWise/README.md:253), [docs/agent_playbook.md:50](/Users/edr/code/JouleWise/docs/agent_playbook.md:50), [docs/decision_log.md:191](/Users/edr/code/JouleWise/docs/decision_log.md:191)).

   The dated restart documents explicitly marked superseded can be archived ([RUN_STATE.md:3](/Users/edr/code/JouleWise/RUN_STATE.md:3)). After campaign close, closed early decision bodies and closed process traces can also move to immutable archival storage, provided the index, hashes, and redirects remain. The queue already proposes this treatment and explicitly protects live decisions such as D-078 ([TASK_QUEUE.md:285](/Users/edr/code/JouleWise/TASK_QUEUE.md:285)).

   Cost/risk: a bad archive would damage provenance, so preserve immutable manifests and never archive live decisions or raw measurement evidence.

6. **F6 — Change after the campaign closes: remove stale promises and make checks semantic.**

   The playbook and plan still describe the expected result as `OK (skipped=10)` from July 8 ([docs/agent_playbook.md:66](/Users/edr/code/JouleWise/docs/agent_playbook.md:66), [AGENT_PLAN.md:237](/Users/edr/code/JouleWise/AGENT_PLAN.md:237)), while README correctly avoids pinning a volatile count ([README.md:197](/Users/edr/code/JouleWise/README.md:197)). `gen_state.py --check` checks generated-byte consistency, not whether the kernel is semantically current with the campaign ([scripts/gen_state.py:795](/Users/edr/code/JouleWise/scripts/gen_state.py:795)).

   First step: replace old test-count prose with a current invariant, and add a post-campaign semantic check for campaign ID, pack family, gate, and next action.

   Cost/risk: documentation churn and a possible false failure during transitions; little direct scientific benefit, but it prevents misleading handoffs.

7. **F7 — Never worth doing for this capstone: add another generic orchestration layer.**

   The repository already requires every new layer, wrapper, skill, or contract to name the failure it addresses, explain why existing controls missed it, and state its budget and retirement condition ([docs/orchestration.md:248](/Users/edr/code/JouleWise/docs/orchestration.md:248)). D-161 has already identified operator-only defenses as over-engineering while preserving physical and evidence safeguards ([docs/decision_log.md:188](/Users/edr/code/JouleWise/docs/decision_log.md:188)).

   First step: reject any new process machinery unless it protects a named paper claim, physics boundary, or evidence-integrity failure. Use a focused check instead.

   Cost/risk: one latent process defect may go undetected, but another broad layer is more likely to consume the remaining schedule than improve the paper.

### WOULD KEEP

1. **Fail-closed physics and evidence rules.** D-161 explicitly keeps refusal for missing calibration, unresolved anchors, absent floors, stale evidence, unfrozen plans, and post-hoc analysis choices ([docs/decision_log.md:188](/Users/edr/code/JouleWise/docs/decision_log.md:188)). Do not simplify these into warnings.

2. **The frozen campaign and narrow research-question set.** D-164 through D-166 pin the model pair, dominance criterion, workload selection, and prefill rule ([docs/decision_log.md:191](/Users/edr/code/JouleWise/docs/decision_log.md:191), [docs/decision_log.md:193](/Users/edr/code/JouleWise/docs/decision_log.md:193)). This prevents the paper from changing its question after seeing data.

3. **Immutable evidence and one-home artifact ownership.** The artifact table distinguishes decisions, deliberation, contracts, run reports, the kernel, and projections ([docs/orchestration.md:148](/Users/edr/code/JouleWise/docs/orchestration.md:148)). Keep that separation even while reducing the number of documents newcomers must read.

4. **Integration and delta review for high-risk changes.** T28 shows these layers finding defects that focused tests missed ([docs/council_log.md:3869](/Users/edr/code/JouleWise/docs/council_log.md:3869), [docs/council_log.md:3877](/Users/edr/code/JouleWise/docs/council_log.md:3877)). They are justified immediately before a physical campaign.

5. **Meta-review that can remove ineffective machinery.** The council record says the Opus refuter tier was dropped after repeated zero unique catches ([docs/council_log.md:31](/Users/edr/code/JouleWise/docs/council_log.md:31), [docs/council_log.md:590](/Users/edr/code/JouleWise/docs/council_log.md:590)). Preserve that willingness to retire process.

### ANOMALIES

- `RUN_STATE.md` presents an old “Mint era” status and Qwen2.5 collection table, though it correctly labels that table historical ([RUN_STATE.md:5187](/Users/edr/code/JouleWise/RUN_STATE.md:5187), [RUN_STATE.md:5215](/Users/edr/code/JouleWise/RUN_STATE.md:5215)). A newcomer can still mistake it for current state.
- The generator check passes while the semantic state is stale. This is a real distinction between projection consistency and truth of the projection.
- The requested merge history returns 126 merge commits since August 1, but only 74 first-parent merges. T28 calls #241, #229, and #246 merged ([RUN_STATE.md:29](/Users/edr/code/JouleWise/RUN_STATE.md:29)); their squash/direct landing shape means `git log --merges` is not a PR counter.
- The production-proof workflow is not automatic, and the canonical local suite failed with 1,787 errors in this sandbox. CI’s ordinary test job also deliberately excludes two modules that run in separate exclusive jobs ([ci.yml:31](/Users/edr/code/JouleWise/.github/workflows/ci.yml:31), [ci.yml:106](/Users/edr/code/JouleWise/.github/workflows/ci.yml:106)); README’s “same suite” wording is directionally true but operationally imprecise.
- The decision-log index/body has good unique-ID parity but duplicate primary headings; the council log has the same addendum/duplicate-entry shape. This is manageable history, not a reason to rewrite it before collection.
- The concurrent fresh-review trace directory was not created or modified by this review; it advanced the repository baseline during the audit.

### OPEN QUESTIONS

1. Is the `WINDOW-COUNCIL-GATE` intentionally still absolute for G2-a, or should G2-a receive an explicit kernel row and clearance path? This changes whether F1 is a simple bookkeeping repair or a real readiness block.

2. Which of the T26 B/C clauses remain open at current head after W-10, #241, #229, and #246? This determines whether F2 is one day of closure or a campaign blocker.

3. Is the advisor’s acceptance bar limited to the narrow D-164/D-165/D-166 research-question set, or is a broader result expected? A broader bar would change the recommendation to cut process work.

4. Must all process traces remain in Git, or is an immutable archived copy with an indexed digest acceptable? This determines how aggressively F5 can reduce newcomer burden.

5. Is the manual D117 production-proof workflow expected to become automatic before the transaction, or is it intentionally deferred? This changes the priority of F4’s post-campaign CI work.

## Residual risk

No desk review can validate the forthcoming Mac measurement, the G2-a physical result, or the final research-question answers; the frozen paper still records result artifacts as pending ([docs/paper/draft-v1.md:189](/Users/edr/code/JouleWise/docs/paper/draft-v1.md:189)). The current T26 census is also not a current-head re-audit, and the local suite result cannot distinguish repository failures from this sandbox’s unusable temporary-directory environment.