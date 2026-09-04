```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The refreshed mission delta is in scope and its focused checks pass, but the mutable bridge manifest can still suppress a required invariant without either gate noticing, so the landing is not landable.",
  "workspace": {
    "base_requested": "b0ed6991c11f3a515ad293760c6dfc031adda8e1",
    "base_mode": "exact",
    "head_start": "adab78aa8f4696cb99958f5c2a4e6ad1f2b7b590",
    "head_end": "adab78aa8f4696cb99958f5c2a4e6ad1f2b7b590",
    "upstream_end": "ec8f780337326f82feb1848a972c4746612da6cc",
    "branch": "feat/2026-09-04-fan-aud-wo-rows"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/aud-wo-rows/02-refuter-merge-base.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "location": "scripts/check-bridge-docs.mjs:69; tests/test_bridge.py:1568",
        "text": "The standalone gate treats the contract's mutable consumer-to-snippet lists as authority, while the Python tests pin only the consumer-key and snippet-key sets, not the required cross-product. Removing `one_hop` from every association and deleting that sentence from all five consumers leaves both the Node gate and all six BridgeDocumentationDriftTests green. The gate therefore cannot enforce the five minimum duplicated invariants it is meant to protect.",
        "counterfactual": "Keep both manifest key sets intact, remove `one_hop` only from every consumer's ID list, and remove its canonical sentence from all consumers: expected rejection; observed Node gate exit 0 and 6/6 Python tests pass."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "location": "tests/test_rpt001_report_slice.py:499",
        "text": "The workstation-path regex requires two consecutive backslashes after a Windows drive letter, so an ordinary absolute path such as `C:\\Users\\example\\private` is accepted. The original macOS-path residue is covered, but the test's stated cross-platform pattern is narrower than intended.",
        "counterfactual": "Append `C:\\Users\\example\\private` to one scanned authored file in a temporary copy: expected test failure; observed acceptance. `/Users/example/private` is correctly rejected."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "base=$(git merge-base origin/main HEAD); test \"$base\" = b0ed6991c11f3a515ad293760c6dfc031adda8e1; test -z \"$(git diff --name-only \"$base\"..HEAD -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json docs/decision_log.md)\"; test \"$(git diff --name-only \"$base\"..HEAD)\" = \"$(printf '%s\\n' docs/contracts/bridge_protocol.md docs/process_traces/2026-09-04-fanout/aud-wo-rows/01-sol-report.md scripts/check-bridge-docs.mjs tests/test_bridge.py tests/test_rpt001_report_slice.py)\"; printf 'scope=pass\\nstate_docs_delta=none\\n'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["scope=pass", "state_docs_delta=none"]},
      "expected": {"exit_code": 0, "tail_regex": "scope=pass.*state_docs_delta=none"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "node scripts/check-bridge-docs.mjs && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_bridge.BridgeDocumentationDriftTests",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["bridge docs check OK (5 consumers, 5 snippets)", "Ran 6 tests in 0.095s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "bridge docs check OK.*Ran 6 tests.*OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_rpt001_report_slice.TestRpt001Artifacts",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 22 tests in 4.385s", "OK (skipped=3)"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 22 tests.*OK \\(skipped=3\\)"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_claims_lint.ClaimsLintFixtureTests.test_unqualified_outcome_dependent_top_up_errors tests.test_claims_lint.ClaimsLintFixtureTests.test_frozen_axi_rules_pass_while_prior_unqualified_rule_still_fails tests.test_calibration_bracketing.CalibrationBracketingTests.test_v2_ledger_candidate_reports_era_rejection_not_custody_failure tests.test_floor_mint_pinsets_schema.FloorMintPinsetsSchemaTests.test_generation_screen_conditionals_match_python_registries tests.test_mint_policy_resolver_guard.MintPolicyResolverGuardTests.test_mint_lane_has_no_copied_bracket_screen_literals",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 5 tests in 0.057s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 5 tests.*OK"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "report_json=$(sed -n '2,/^```$/p' docs/process_traces/2026-09-04-fanout/aud-wo-rows/01-sol-report.md | sed '$d'); test \"$(head -n 1 docs/process_traces/2026-09-04-fanout/aud-wo-rows/01-sol-report.md)\" = '```json' && test \"$(printf '%s' \"$report_json\" | wc -c | tr -d ' ')\" -le 8192 && printf '%s' \"$report_json\" | jq -e '.schema == \"claude-codex-report/v1\" and .genre == \"implementation\" and (.summary | length > 0) and (.pathspec | type == \"array\") and (.verification | type == \"array\") and (.flags | type == \"array\")' >/dev/null && printf 'report_contract=pass\\n'; git diff --check $(git merge-base origin/main HEAD)..HEAD && printf 'diff_check=pass\\n'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["report_contract=pass", "diff_check=pass"]},
      "expected": {"exit_code": 0, "tail_regex": "report_contract=pass.*diff_check=pass"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "python3 -c 'import json,pathlib,re,subprocess; p=pathlib.Path(\"docs/process_traces/2026-09-04-fanout/aud-wo-rows/02-refuter-merge-base.md\"); s=p.read_text(); m=re.match(r\"^```json\\n([\\s\\S]*?)\\n```\",s); assert m and len(m.group(1).encode())<=8192; o=json.loads(m.group(1)); assert o[\"schema\"]==\"claude-codex-report/v1\" and o[\"genre\"]==\"review\"; d=subprocess.run([\"git\",\"diff\",\"--no-index\",\"--check\",\"/dev/null\",str(p)],capture_output=True,text=True); assert d.returncode in (0,1) and not d.stdout and not d.stderr; print(\"report_contract=pass\\nenvelope_bytes_le_8192\\ndiff_check=pass\")'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["report_contract=pass", "envelope_bytes_le_8192", "diff_check=pass"]},
      "expected": {"exit_code": 0, "tail_regex": "report_contract=pass.*envelope_bytes_le_8192.*diff_check=pass"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Three private-corpus tests skipped because the runs corpus is unavailable; the explicit preflight prohibited the repository-wide suite.",
      "needs": "The landing lead may run broader or private-corpus gates if required by final-head policy."
    }
  ]
}
```

## Findings

### F1 — blocker

The manifest validates the values it supplies itself. In a temporary copy I preserved the five snippet keys and five consumer keys, removed only `one_hop` from every consumer's required-ID list, and removed the corresponding sentence from every consumer. `node scripts/check-bridge-docs.mjs` returned success, and the complete `BridgeDocumentationDriftTests` class still reported 6/6 passing. The script or an independent test must pin every required consumer/snippet association rather than trusting those associations from the mutable contract.

The new negative test itself is sound against a simpler implementation reversion: changing the checker's `if (count !== 1)` branch to `if (false)` made `test_standalone_checker_passes_and_rejects_consumer_drift` fail. It does not cover coordinated contract/consumer drift, which is the blocking input above.

### F2 — should_fix

The regex correctly rejects `/Users/example/private` and `/home/...`, but it accepts the normal single-backslash Windows form `C:\Users\example\private`. Change the drive-letter branch to match one literal backslash and add that exact input as a negative fixture.

## Counterfactual evidence

The repaired prior-round cases were exercised, not inferred:

- Configured-token sourcing: a runtime mutation returning the configured cap `97` instead of the two-line token artifact made `test_realized_tokens_come_from_artifact_without_stop_inference` fail. Status: cured.
- Default evidence handoff: adding `docs/contracts/evidence_handoff.md` in a temporary fixture made the new absence test fail. Status: cured.
- Workstation absolute path: adding `/Users/example/private` made the authored-source scan fail; the Windows variant is F2. Status: macOS/Linux case cured, Windows case open.
- Pristine clone: instrumentation observed that the clone destination did not exist before `git clone`; committing a one-line dependency on an untracked `local-only-required-input` in a temporary source clone made the nested pristine-clone test fail. Status: occupied-root and untracked-input blockers cured.
- Standalone checker: disabling its occurrence-count rejection made the new checker test fail, but removing a requirement through the trusted mutable association lists passed the Node command and all six Python tests. Status: direct consumer-drift counterfactual cured; spoofable/trusted-manifest blocker open as F1.

No previous `02-refuter-merge-base.md` was present in the mission directory or any Git ref, so these statuses use the concrete previous-round blocker classes named in the assignment.

## Residual risk

The three skipped report tests require the private runs corpus. No whole-suite discovery was run, exactly as required by the preflight rule.
