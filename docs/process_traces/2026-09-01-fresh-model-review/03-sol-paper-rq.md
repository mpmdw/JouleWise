```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The repository can produce a defensible capstone in ten days, but an unconditional headline needs the inference fiducial and the paper should be rebuilt section-wise rather than mechanically patched.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "672b995fd258e0a87e7abd4f9b76f626598e6e39",
    "head_end": "3b3839c0636bfb5e6fe5537178b1929551dac139",
    "upstream_end": "3b3839c0636bfb5e6fe5537178b1929551dac139",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [
    "docs/process_traces/2026-09-01-fresh-model-review/"
  ],
  "verdict": {
    "overall": "conditionally fit",
    "biggest_change": "Make the inserted-gap inference fiducial a gate for any unconditional attribution-dominance conclusion.",
    "biggest_protection": "Preserve the immutable, preregistered, per-cell, fail-closed evidence chain.",
    "findings": [
      {"id":"F1","severity":"blocker","title":"Untested pulse-to-inference transfer blocks an unconditional headline"},
      {"id":"F2","severity":"blocker","title":"Generated work-selection state and G2-b readiness do not agree with the current campaign plan"},
      {"id":"F3","severity":"should_fix","title":"Write a fresh successor paper around the issued results instead of mechanically applying all round-7 blocks"},
      {"id":"F4","severity":"should_fix","title":"The statistical unit and dependence assumptions need an explicit sensitivity analysis"},
      {"id":"F5","severity":"should_fix","title":"The new dominance ratio is acceptable as an operational falsifier but is absent from the frozen draft"},
      {"id":"F6","severity":"should_fix","title":"Keep the narrow answer set and demote C5-1.1 to a fixed-pair demonstration"},
      {"id":"F7","severity":"should_fix","title":"Use any remaining desk capacity to strengthen auditability, not to add another measurement question"}
    ]
  },
  "verification": [
    {
      "id":"V1",
      "kind":"inspection",
      "cmd":"git status --short --branch",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["## main...origin/main","?? docs/process_traces/2026-09-01-fresh-model-review/"]},
      "expected":{"exit_code":0,"tail_regex":"## main\\.\\.\\.origin/main"}
    },
    {
      "id":"V2",
      "kind":"test",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_d117_contrast_v5_pack tests.test_select_g2a_prefill_length tests.test_paper_terms_lint tests.test_render_results_fills tests.test_paper_build",
      "cwd":".",
      "observed":{"result":"fail","exit_code":1,"tail":["Ran 59 tests in 1.408s","","FAILED (errors=41, skipped=2)"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id":"V3",
      "kind":"test",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_golden_readback_ratio_predicate_and_zero_denominator_refusal tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_common_mode_replay_matches_independent_retained_fixture_calculation tests.test_select_g2a_prefill_length.SelectG2APrefillLengthTests.test_reducer_constant_is_imported_not_restated tests.test_paper_terms_lint.RealDocumentRegressionTests.test_plan_is_lint_clean tests.test_render_results_fills.DerivationTests.test_branch_predicates_and_zero_ratio_denominator_fail_closed",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["Ran 5 tests in 0.506s","","OK"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id":"V4",
      "kind":"inspection",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_state.py --check",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":[]},
      "expected":{"exit_code":0,"tail_regex":"^$"}
    }
  ],
  "flags": [
    {
      "id":"G1",
      "kind":"baseline_drift",
      "level":"blocking",
      "text":"The generated kernel projections still gate all quiet-Mac work and name retired Qwen2.5 packs while the current intake declares Qwen3 _v5 as next.",
      "needs":"Reconcile the state kernel and transaction authority before G2-b or the production transaction."
    },
    {
      "id":"G2",
      "kind":"environment",
      "level":"nonblocking",
      "text":"The read-only execution environment has no usable temporary directory; 41 targeted tests errored during tempfile setup rather than at assertions.",
      "needs":"Rerun the targeted batch or canonical suite in a normal writable test environment."
    },
    {
      "id":"G3",
      "kind":"verification_gap",
      "level":"nonblocking",
      "text":"The specialized D117 production-proof workflow is manual-only because its fixture has drifted from current main.",
      "needs":"Repair or explicitly run that proof before treating ordinary CI as complete production-path verification."
    }
  ]
}
```

## Findings

Verdict: conditionally yes—the repository is fit to produce a defensible undergraduate capstone in roughly ten days, but not an unconditional ICPE-style attribution claim while its pulse-derived timing bound remains untested on inference (`docs/paper/draft-v1.md:19-21`, `docs/paper/draft-v1.md:292-300`). The chosen answer set is the right paper: attribution dominance, one explicitly fixed-pair comparison, and the short-prefill negative; the coverage map itself records that scope (`docs/research_question_coverage-2026-08-28.md:190-204`). The single biggest change is to make the inserted known-gap inference check a gate for the headline. The single biggest thing to protect is the immutable, preregistered, per-cell, fail-closed evidence chain (`AGENTS.md:100-103`, `docs/paper/draft-v1.md:212-235`). The “documenting instead of measuring” concern is partly substantiated: the process produced real corrections, but the paper apparatus has reached a point where its own final review says it is not usable despite 81 governed edit blocks (`docs/process_traces/2026-08-31-registry-v5/12-PARK-DISPOSITION.md:1-35`).

### Ranked changes

**F1 — Change after the campaign closes: make the transfer fiducial a paper gate.**

- Observation: the draft says the pulse-to-inference transfer is assumed, not tested, while all three blind reviewers called that the leading weakness and unanimously selected the inserted-gap check as the best use of one night (`docs/paper/draft-v1.md:294-300`, `docs/process_traces/2026-08-28-reviewer-panel/04-SYNTHESIS.md:18-25`, `docs/process_traces/2026-08-28-reviewer-panel/04-SYNTHESIS.md:246-264`). D-163 already gives this check the first post-campaign window (`docs/decision_log.md:190`).
- Why it matters: without it, a positive ratio means only that the pulse-derived envelope dominates inside the registered calculation—not that the envelope correctly describes prefill/decode edges during inference.
- First step, under one day: before the transaction, freeze the fiducial’s residual comparison, output wording, and pass/refuse rule, and confirm that its existing-estimator implementation is actually runnable. Then run it before finalizing the conclusion. If it cannot run, make the title and conclusion explicitly conditional.
- Cost/risk: less than one measurement night, but it can falsify or narrow the headline. That is scientific risk worth taking.

**F2 — Change now, before the campaign: issue one authoritative transaction-readiness state.**

- Observation: the current intake says G2-a and a Qwen3 `_v5` transaction are next (`RUN_STATE.md:13-50`), while the generated gate says no quiet-Mac work is permitted and names the retired Qwen2.5 packs (`RUN_STATE.md:5036-5065`, `TASK_QUEUE.md:572-589`). The G2 runsheet separately says no G2-b command is authorized until its real supply and confirmation pair are cured, and its governed chain still labels the supply channel an open defect (`docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:92-121`, `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:781-788`).
- Why it matters: one lost transaction night now threatens the paper more than any prose defect. `gen_state.py --check` passing only proves that generated text matches the stale kernel; it does not prove that the kernel matches D-164 through D-166.
- First step, under one day: reconcile the kernel, queue, stop gate, G2-b supply, aggregate-floor path, and confirmation-pair channel into one lead-issued readiness card. Do not begin G2-b until all resolve to the same Qwen3 pack.
- Cost/risk: up to one desk day and possibly one-night delay; the benefit is avoiding a week-ending invalid or unauthorised transaction.

**F3 — Change after campaign close: draft the `_v5` paper section-wise from a clean successor file.**

- Observation: the frozen draft’s abstract, research question, campaign, tables, discussion, and conclusion still describe `_v4`, Qwen2.5, fixed p256, and the superseded any-exceedance falsifier (`docs/paper/draft-v1.md:7-31`, `docs/paper/draft-v1.md:185-200`, `docs/paper/draft-v1.md:239-290`, `docs/paper/draft-v1.md:354-358`). The round-7 apparatus is parked at 59/81 blocks passing with three blockers and thirteen should-fixes (`docs/process_traces/2026-08-31-registry-v5/12-PARK-DISPOSITION.md:1-35`).
- Why it matters: mechanically applying dozens of substitutions to prose whose scientific center has changed is more likely to preserve contradictions than to save time.
- First step, under one day: make a section-level survival map. Retain the calibration mechanics, cell-bound construction, admission/refusal rules, related-work core, and reproduction appendix (`docs/paper/draft-v1.md:33-180`, `docs/paper/draft-v1.md:212-237`, `docs/paper/draft-v1.md:320-352`, `docs/paper/draft-v1.md:394-652`). Rewrite the abstract, introduction/RQs, results, discussion, and conclusion around issued `_v5` artifacts.
- Cost/risk: roughly one to two writing days and a risk of dropping a governed disclosure. Use the fill registry as the supplier/claim audit ledger and the structural sheets as a final checklist, not as the prose generator.

**F4 — Change before results interpretation: specify the independent statistical unit and shared-dependence sensitivity.**

- Observation: the draft applies Student-*t* inference to ten blocks but does not justify treating blocks from one long session as independent (`docs/paper/draft-v1.md:260-264`). The reviewer synthesis notes shared calibration, thermal trajectory, background conditions, and sampler correlation, which a deterministic drift allowance does not remove (`docs/process_traces/2026-08-28-reviewer-panel/04-SYNTHESIS.md:142-147`). The appendix also gives a “95/95” interpretation that assumes 59 independent pulse draws, while the new excursion analysis explicitly says its index analysis does not prove independence (`docs/paper/draft-v1.md:642-652`, `docs/paper/round7/excursion-decomposition.md:133-140`).
- Why it matters: a hostile reviewer can accept conservative interval arithmetic and still reject the reported *p*-values or tolerance language.
- First step, under one day: add an uncertainty-and-dependence table naming each quantity’s independent unit, what is shared by session/block/member, degrees of freedom, missing-block rule, and a sensitivity result under plausible block clustering. Relabel “95/95” as a sample-maximum interpretation unless independence is defended.
- Cost/risk: the inferential claim may become wider or descriptive. That is preferable to presenting unjustified precision.

**F5 — Change after campaign close: install the actual ratio falsifier and describe it as an operational materiality rule.**

- Observation: D-165 preregisters \(R=\) corner-widened unguarded floor divided by point-only unguarded floor, requires \(R\ge2\) for every component and cell, refuses a zero denominator, and requires the shared-error ratio \(R_{cm}\) (`docs/decision_log.md:192`, `configs/campaigns/d117_contrast_v5/generate_configs.py:496-579`, `configs/campaigns/d117_contrast_v5/generate_configs.py:591-612`). The registered common-mode replay authenticates the operative bound and enumerates one shared sign plus block-local signs (`configs/campaigns/d117_contrast_v5/generate_configs.py:683-772`). The frozen draft still contains the superseded “any exceedance” rule (`docs/paper/draft-v1.md:21`, `docs/paper/draft-v1.md:185`); the ratio exists only in code, the fill registry, and structural sheets (`docs/paper/results-fill-registry.md:210-228`, `docs/paper/round7/structural-edits.md:18-84`).
- Why it matters: a reviewer can accept this as a preregistered falsifier—meaning a rule whose failure withdraws the claim—because it has physical operands, an all-cells quantifier, a zero-denominator refusal, and a shared-error sensitivity. But \(2\) is a chosen twofold materiality threshold, not a confidence level or a test of transfer.
- First step, under one day: write one reader-facing Methods paragraph, one eight-row component table, and one sentence stating that \(R_{cm}<2\) withdraws the sentence. Explicitly call the factor of two an operational safety factor.
- Cost/risk: additional notation and explanation. Do not let \(R_{cm}\) be portrayed as solving session dependence or pulse-to-inference transfer.

**F6 — Never worth doing before this submission: add another measurement question.**

- Observation: the coverage map has 41 instrument-answerable questions with no route, but each needs its own cells and measurement night; even its three “cheapest” promotions require new experimental axes, with quantization estimated at four nights (`docs/research_question_coverage-2026-08-28.md:166-180`, `docs/research_question_coverage-2026-08-28.md:198-214`). C5-1.1 is explicitly capped at pairwise evidence unless a larger model set is preregistered (`docs/research_question_registry.md:64`), and `_v5` supplies only the fixed Qwen3 8B-versus-1.7B pair (`docs/research_question_coverage-2026-08-28.md:196`, `docs/research_question_coverage-2026-08-28.md:204`).
- Why it matters: calling one pair “energy ordered by parameter count” invites an easy generalization attack. Adding a fourth research answer now would displace validity work and paper completion.
- First step, under one day: rename C5-1.1 in reader-facing prose to “a fixed-pair demonstration of the decision rule.” Keep “active-parameter scaling” only as the registry identifier.
- Cost/risk: the paper sounds less expansive. It becomes considerably more defensible.

**F7 — Change after campaign close if time permits: promote auditability, not another scientific result.**

- Observation: `RQ-AUDITABLE-EVIDENCE` is already an answered-L1 capability claim and is classified as answerable at the desk (`docs/research_question_registry.md:56`, `docs/research_question_coverage-2026-08-28.md:49`). The draft candidly says the evidence is unreleased and the floor-to-extraction link is not independently re-reducible (`docs/paper/draft-v1.md:346-352`, `docs/paper/draft-v1.md:394-415`).
- Why it matters: closing or sharply delimiting that chain would strengthen the artifact contribution without consuming the only measurement machine or pretending to add a fourth RQ.
- First step, under one day: issue the exact archive manifest and locators, then decide whether FLOOR-BIND-01 can close before the advisor version. If not, preserve the current L1 limitation verbatim.
- Cost/risk: packaging and external-owner time; it may not fit before the meeting.

### The three claims a hostile reviewer attacks first

| Claim | Does the evidence plan answer it? |
|---|---|
| “Boundary placement dominates repeatability during inference.” | \(R\) and \(R_{cm}\) answer dominance inside the registered envelopes, but not whether pulse-derived envelopes transfer to inference. Only the inserted-gap fiducial addresses that (`docs/decision_log.md:192`, `docs/paper/draft-v1.md:294-300`). |
| “The ten ABBA blocks support Student-*t* directional inference.” | Not fully. ABBA counterbalances approximately linear order drift, but one session can leave shared calibration, thermal, and serial dependence (`docs/paper/draft-v1.md:227-229`, `docs/process_traces/2026-08-28-reviewer-panel/04-SYNTHESIS.md:142-147`). |
| “Energy is ordered by parameter count.” | No beyond the one fixed Qwen3 pair. The registry itself caps C5-1.1 at pairwise evidence, so the paper should report a pair-specific decision rather than a scaling relationship (`docs/research_question_registry.md:64`, `docs/research_question_coverage-2026-08-28.md:69-72`). |

### Would keep

- Immutable raw evidence, frozen plans, and preserved failed attempts. These prevent favorable-subset selection and are central scientific controls, not merely repository ceremony (`AGENTS.md:100-103`, `docs/paper/draft-v1.md:231-235`).
- Per-cell floors with no transport across model, phase, or prompt length. This is the paper’s most defensible metrology choice (`docs/paper/draft-v1.md:109-177`, `docs/paper/draft-v1.md:260-262`).
- Separate absolute and ABBA comparative components, plus the new shared-error replay. Simplifying these into one uncertainty number would hide the very attribution structure being tested (`docs/paper/draft-v1.md:117-177`, `configs/campaigns/d117_contrast_v5/generate_configs.py:636-772`).
- Printed refusals and the retained 37-of-50 short-prefill negative. This is a genuine result about the instrument’s time resolution, not an embarrassing failed comparison (`docs/paper/draft-v1.md:245-256`, `docs/research_question_coverage-2026-08-28.md:200-202`).
- G2-a’s deterministic four-rung selection and fallback. It fixes the prefill length from authenticated counts before the pack is authored and distinguishes physical non-resolvability from the stricter preregistration refusal (`docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:441-478`, `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:487-525`).

### Anomalies

- The research-question registry still names a frozen `_v4` transaction and the old falsifier, despite D-164/D-165 and the coverage map describing `_v5` and the ratio rule (`docs/research_question_registry.md:82`, `docs/decision_log.md:191-192`, `docs/research_question_coverage-2026-08-28.md:61`).
- The fill checklist says DG-071/DG-075 statistics are proposed but unratified, while the later ratification explicitly fixes both statistics (`docs/paper/round7/fill-checklist.md:241-249`, `docs/paper/round7/fill-checklist.md:366-368`, `docs/process_traces/2026-08-31-registry-v5/02-dg071-dg075-ratification.md:1-20`).
- The frozen draft says the sampler pauses between records, but retained evidence says records tile without a pause (`docs/paper/draft-v1.md:256`, `docs/process_traces/2026-08-31-registry-v5/02-dg071-dg075-ratification.md:13-16`).
- Ordinary CI runs the normal test shards, but the specialized D117 production proof is manual-only because its fixture drifted from main (`.github/workflows/ci.yml:1-37`, `.github/workflows/d117-production-proof.yml:1-13`).
- The paper-term regression test points only at `retensing-plan.md`; the parked disposition says the structural sheet has never been linted successfully (`tests/test_paper_terms_lint.py:11-15`, `docs/process_traces/2026-08-31-registry-v5/12-PARK-DISPOSITION.md:18-28`).

### Open questions for the owner

1. Is the target the strongest defensible capstone report, or something intended to survive venue-style peer review? The former can carry a clearly conditional transfer limitation; the latter should gate its headline on the fiducial.
2. Is the inserted-gap implementation already runnable immediately after `_v5`, or is it merely registered? If it is not runnable, the title should be reframed before results arrive.
3. Can the transaction slip one night if reconciling the kernel and G2-b supply requires it? If yes, take the desk day; if no, prepare a narrower explicit authority record.
4. Must the evidence archive be public and independently re-reducible for the advisor version? That determines whether F7 is a release task or only a limitations paragraph.
5. Does the advisor expect C5-1.1 to be called a research answer? If so, I would still label it “pairwise-only”; otherwise, present it simply as the method’s worked demonstration.

## Residual risk

No `_v5` result exists yet, so this review can assess the design and claim discipline but not whether the estimates, intervals, floors, ratios, or refusals actually cohere; the draft itself still marks those artifacts pending (`docs/paper/draft-v1.md:239-290`). The canonical suite could not be rerun in this read-only environment because temporary-directory creation is unavailable; five central no-temp checks passed, but ordinary CI and the specialized production proof remain the authoritative verification routes. The retained corpora were treated as immutable and were not exhaustively re-reduced; numerical assessment relied on the governed summaries, registrations, fixtures, and existing independent reviewer trace.