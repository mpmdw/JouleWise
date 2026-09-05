```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Reconciled D-174 fallback retirement without dropping artifact checks; all four authorized modules pass.",
  "workspace": {
    "base_requested": "5e262164",
    "base_mode": "exact",
    "head_start": "5e262164112056ec7ba5a5237e2eb7672c63a1cc",
    "head_end": "5e262164112056ec7ba5a5237e2eb7672c63a1cc",
    "upstream_end": "5e262164112056ec7ba5a5237e2eb7672c63a1cc",
    "branch": "feat/2026-09-05-paper-m"
  },
  "pathspec": [
    "scripts/check_paper_round7_artifacts.py",
    "tests/test_paper_round7_artifacts.py",
    "docs/paper/results-fill-registry.md",
    "docs/process_traces/2026-09-05-paper-m/11-round7-checker-reconciliation-report.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest -v tests.test_paper_round7_artifacts > /private/tmp/paper-m-r7-reconciliation-tests.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 67 tests in 613.711s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 67 tests in [0-9.]+s\\n\\nOK$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest -v tests.test_select_outcome_branches > /private/tmp/paper-m-selector-reconciliation-tests.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 5 tests in 0.810s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 5 tests in [0-9.]+s\\n\\nOK$"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest -v tests.test_paper_terms_lint > /private/tmp/paper-m-terms-reconciliation-tests.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 16 tests in 2.891s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 16 tests in [0-9.]+s\\n\\nOK$"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest -v tests.test_paper_first_use_ledger > /private/tmp/paper-m-ledger-reconciliation-tests.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 11 tests in 2.389s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 11 tests in [0-9.]+s\\n\\nOK$"
      }
    }
  ],
  "flags": []
}
```

## Change

The paper-M fallback retired 228 registry entries while the merged paper-L parser still required every DX row to have its pre-fallback fill rule and freeze label. DX-002 was the first rejection. In `test_checker_accepts_pe01_pins_and_placement`, `digest_half` caught that `RegistryError` and returned `None`; the subsequent `spec.rows` access caused the secondary `AttributeError`. Accepting the valid retirement disposition fixes that root cause. No null guard, exception suppression, row restoration, or relaxed test assertion was added.

The governing disposition is D-174 and `docs/process_traces/2026-09-05-readiness/02-magistrate-ruling-fallback.md`. Fixtures use the rows actually active under the selector's sole METHODS_DIAGNOSTIC outcome. The selector itself needs no implementation change.

| Check or fixture | Change and why it is not a weakening |
|---|---|
| DX fill rule and freeze label | Active DX rows still require their exact MEASURED/DERIVE rule and full freeze label. RETIRED_FALLBACK requires the exact 2026-09-05 D-174 note, the original expected fill rule, and the original full freeze label. The closed 19-row set, order, campaigns, render directives, field references, pending-marker prohibition and identity binding remain enforced. |
| Registry retirement notes | Adds validation for all 228 dated dispositions, including the two metadata entries. Preserves the existing standard disposition, four method-moved dispositions and PG-03's exact consolidated tombstone. Escaped Markdown table pipes and DS-08a-style IDs are recognized. Each dated note is independently corrupted in regression tests and must be rejected. |
| Article retirement placement | Adds 228 comparisons over the complete article, including comments, rejecting retired identifiers and tokens. Wildcard metatokens match concrete tokens. Every retired site is individually reinserted in a regression; representative DX, moved-method, tombstone and bracket-token cases also exercise the CLI. |
| DX literal and prose checks | Exact retired FILL placements now fail even if the value matches or is commented. The prose scanner still examines every historical nonidentity DX rendering; retired renderings fail with or without their own marker. Active renderings keep the original exact-value, token-boundary and immediately-preceding-marker checks. |
| Active placement census | The four active nonidentity rows DX-010–013 replace the obsolete 16-row mandatory census. Removing one active marker still fails and prints 3/4. The standing-sentence requirement remains enforced. Appendix DERIVE rows retain producer digest/size and unique-location checks; a retired appendix binding is subject to retirement-note/absence checks rather than an active placement requirement. |
| Positive and negative literal fixtures | Bare/backticked values and ambiguous suffixes now use genuinely active DX-010/011/012 instead of retired DX-020/026. The separator rejection uses active DX-010. Existing numerical/type/rounding/gate tests against retired AQ artifacts remain intact. |
| Prose and appendix fixtures | The valid prose fixture contains the four active DX rows. The PE-01 appendix location is read from the registry (currently A.6), fixing stale A.7 assumptions both when creating a future B.2 binding and when including the real appendix in prose fixtures. Missing, duplicate, misplaced and incorrectly pinned active appendix bindings still fail. |
| Comparison census and preserved evidence | The original 184 digest/literal comparisons remain, plus 228 retirement comparisons = 412. The same three XD/F4/AQ byte-replay comparisons bring the total to 415. Source digests/sizes, supplier resolution, numeric typing and rendering, all three artifact gates, all 118 figure marks and geometry tolerances, unavailable-input disposition and replay byte identity are unchanged. No existing active MEASURED/DERIVE/EXTRACT check was removed. |

The registry change only documents these enforcement semantics and the retained legacy standing-sentence boundary. Inspection confirmed every registry table row is byte-identical to HEAD, including all 228 retirements. No artifact bytes, source pins, manuscript, selector or external corpus were modified.

## Verification notes

Only the four requested modules were run, sequentially, with `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise`. Bytecode writes were disabled. No discovery suite, new agent, Claude/Codex launcher, hardware acquisition or commit was run.

During implementation, short preliminary runs exposed the alternate retirement-note forms and letter-suffixed DS identifier. Two subsequent development runs were interrupted after identifying stale fixture assumptions, before a complete retained-corpus replay. Those runs are not acceptance evidence; the complete final commands and exact tails are recorded in the envelope.

The pre-fallback fill checklist remains archival and outside this write scope; the registry's fallback amendment explicitly governs active placement. The checker continues using its legacy standing-sentence boundary when marker-based DX prose is supplied.

## Residual risk

Retired identifiers/tokens are checked throughout the article. Bare numeric values are attributable to retired DX rows only within the bounded DX prose regions; common numbers elsewhere cannot uniquely identify a retired value-site. This preserves the existing prose-check boundary while adding explicit retirement rejection.

Lead-owned final diff review and integration approval remain outstanding. Next exact step: review this scoped diff and the four passing module records; no commit was created.

