```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Delta re-audit is NOT CLEAN: the cures are factually faithful, but they introduce late-built terms and leave a contradictory transfer-predicate build note.",
  "workspace": {
    "base_requested": "27b6f69c",
    "base_mode": "exact",
    "head_start": "27b6f69cb344028fd3e0e6fa8fbe9d9058827086",
    "head_end": "27b6f69cb344028fd3e0e6fa8fbe9d9058827086",
    "upstream_end": "27b6f69cb344028fd3e0e6fa8fbe9d9058827086",
    "branch": "feat/2026-09-04-paper-k"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-paper-k/02-delta-re-audit-round-1.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "result": "NOT CLEAN",
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "title": "Cures create late-construction first uses",
        "locations": ["draft-v2-skeleton.md:29", "draft-v2-skeleton.md:64", "draft-v2-skeleton.md:116", "draft-v2-skeleton.md:139"]
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "A surviving build note restores the ruled-out transfer predicate",
        "locations": ["draft-v2-skeleton.md:1158"]
      }
    ],
    "same_signature": {
      "paper_j_classes_surviving": ["late construction", "stale contradictory editorial instruction"],
      "other_classes_checked": ["orphaned gloss", "undeclared synonym", "physical singular/plural mismatch", "unused alias", "stale ledger vocabulary", "synonym drift"]
    },
    "title": {
      "current": "faithful and one-line reversible, but less explicit about sensitivity",
      "recommendation": "JouleWise: Timing Sensitivity of Phase-Energy Assignments on Apple Silicon",
      "decision_owner": "magistrate"
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["..........", "----------------------------------------------------------------------", "Ran 10 tests in 1.751s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 10 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["....", "----------------------------------------------------------------------", "Ran 4 tests in 1.373s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 4 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_select_outcome_branches",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["...", "----------------------------------------------------------------------", "Ran 3 tests in 0.487s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 3 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git show 27b6f69c^:docs/paper/draft-v2-skeleton.md | rg -o '\\[FILL:' | wc -l; rg -o '\\[FILL:' docs/paper/draft-v2-skeleton.md | wc -l; git show 27b6f69c^:docs/paper/draft-v2-skeleton.md | rg -o '\\[FILL:TR-01\\]' | wc -l; rg -o -F 'Transfer of the pulse-derived timing allowance to inference was not tested.' docs/paper/draft-v2-skeleton.md | wc -l; git show 27b6f69c^:docs/paper/draft-v2-skeleton.md | rg '^<!-- OUTCOME-BRANCH' | shasum -a 256; rg '^<!-- OUTCOME-BRANCH' docs/paper/draft-v2-skeleton.md | shasum -a 256; rg -c '^<!-- OUTCOME-BRANCH' docs/paper/draft-v2-skeleton.md; tail -n 1 docs/paper/draft-v2-skeleton.md",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["     140", "     131", "       9", "       9", "5a0d0e0374916eaa07dd7e5bb85032827a720842ed4b4011e693e41a90a05b42  -", "5a0d0e0374916eaa07dd7e5bb85032827a720842ed4b4011e693e41a90a05b42  -", "24", "a failure. Terms inventoried: 261; FAILS: 0."]},
      "expected": {"exit_code": 0, "tail_regex": " +140\\n +131\\n +9\\n +9\\n([0-9a-f]{64})  -\\n\\1  -\\n24\\na failure\\. Terms inventoried: 261; FAILS: 0\\."}
    }
  ],
  "flags": [
    {
      "id": "F3",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "Ruling 17 did not order the one-line title change; both options are faithful.",
      "needs": "Magistrate chooses; recommend astra 03-F1's sensitivity title."
    },
    {
      "id": "F4",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "D-166's prompt-0 prose is prospective; 27b6f69c does not regenerate the cycling contrast generator.",
      "needs": "Complete the ordered config/identity/custody supersession before collection."
    }
  ]
}
```

## Findings

**F1 — should_fix — late-built terms in cures.** Items 2/6 put “registered timing domain” and “block-level energy allowances” into every Abstract branch without defining registered, block, or allowance; item 3 repeats the first phrase before construction. Item 18 presents “Same-model null A/B/B/A blocks, with A = B” before the four-run order at line 138. Item 7 uses “the floor packs set A = B” at line 139 but defines floor packs only at line 292. The ledger calls these first uses glossed. This is paper-J's late-construction class; the green test does not cover the phrases.

**F2 — should_fix — retired transfer predicate survives.** Lines 1158–1163 say “BUILD AFTER CAMPAIGN AND TRANSFER FIDUCIAL” and “the headline remains conditional on it.” This conflicts with 17 §A's “no late-window predicate,” all nine fixed sentences, and line 1202. Delete or retensor the note; non-gating future work may remain.

**Verdict: NOT CLEAN.** No blocker; one sentence/table cure and one comment cure should close the round.

Cure-ledger audit:

| Items | Result |
|---|---|
| 1 | Unordered, faithful, one-line reversible. Astra's “Timing Sensitivity of Phase-Energy Assignments on Apple Silicon” is clearer; magistrate decides. |
| 2–5 | D-078 is faithful: held-average condition, no physical/future/transfer coverage, non-composed [8,10] J enclosure. §B “does not bound physical energy” becomes “not a bound on physical phase energy,” without scope change. F1 applies; no containment claim survives. |
| 6–9 | D-165 is faithful: energy sign, no physical replay/conservatism, comparative-only absolute N/A, v2, unchanged 8+4 census/threshold. F1 applies; no cancellation rationale survives. |
| 10–11 | D-083 is faithful. Lexical deviation: §B “symmetric metrology interval estimate±h” becomes “symmetric measurement interval with half-width h.” The defined interval, max(F,h+B), actual endpoints, and non-gating/neither-necessary-nor-sufficient status remain. |
| 12–14 | The dictated TR-01 sentence is exact at all nine sites; selector/registry preserve three selected limitations and remove the lookup. F2 is the contradictory surviving editorial instruction. |
| 15 | Code-faithful: support intervals use constant `power_w × overlap`; both interpolation helpers return 0 for positive native intervals. |
| 16 | Code-faithful: stochastic terms dispatch only for `energy_request_j`; `phase_energy_j.*` gets none, so phase contrasts use repeat SE and separate deterministic bounds. |
| 17 | Code-faithful: `_T_CRITICAL_95[4]=2.776`; the expression is 4.8081730418 J, printed 4.808173 J. |
| 18 | Same-model repeat/null floors versus the two-model science contrast is correct; F1 applies to the unbuilt A/B/B/A label. |
| 19 | D-166's disclaimer is exact: “The comparison supports this fixed prompt and makes no prompt-population generality claim.” It is prospective as §B requires; see flag F4. |
| 20–24 | Ratio-frequency, model/coverage, Holm, midpoint-symmetry, diagnostic-support and historical-support qualifications are faithful and introduce no additional defect. |

Retired-phrase sweep: zero occurrences of the five specified phrases. Line 1276's qualified “cancels it exactly only when the A and B time-midpoint sums match” is consistent, not the retired unconditional claim. Physical-phase wording occurs only in disclaimers. Outcome markers are parent-identical (V4); all selector outcomes pass.

Same-signature statement: F1 repeats paper-J's late-construction class; F2 is a stale contradictory editorial-instruction variant. No new orphaned gloss, undeclared synonym, singular/plural mismatch, unused alias, stale ledger-vocabulary, or synonym-drift instance was found.

## Residual risk

No discovery suite, corpus replay, generator execution, hardware work, or other model session ran. Code verification was source inspection limited to the three requested behavior claims. D-166's separately ordered prospective generator/custody regeneration remains outside this paper-only delta.
