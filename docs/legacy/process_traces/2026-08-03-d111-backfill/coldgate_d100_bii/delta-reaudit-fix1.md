```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "FAIL: A2 and the two prescribed V2 probes are fixed, but nested-content closure remains bypassable and pathological depth escapes as RecursionError.",
  "workspace": {
    "base_requested": "a6ce7af",
    "base_mode": "exact",
    "head_start": "a6ce7af7c6c4e1119d6c4365fb63ce4482f9e246",
    "head_end": "a6ce7af7c6c4e1119d6c4365fb63ce4482f9e246",
    "upstream_end": "a6ce7af7c6c4e1119d6c4365fb63ce4482f9e246",
    "branch": "impl/d100-bii-binding"
  },
  "pathspec": [],
  "unowned_dirty": [
    "joulewise/salvage_dangler.py",
    "tests/test_run_campaign.py",
    "tests/test_salvage_dangler.py",
    "BRIEF.md"
  ],
  "verdict": {
    "overall": "fail",
    "blocker_present": true,
    "fix_fidelity": {
      "A1": "fail: prescribed probes refuse, but equivalent nested-content bypasses license",
      "A2": "pass"
    },
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "file": "joulewise/salvage_dangler.py:526",
        "title": "Recursive classification is still a key denylist, not fail-closed content classification",
        "scenario": "environment_admission.failure containing workload output, an NFKC-equivalent fullwidth model_output key, unknown empty/scalar children, and matching event/summary failure_reason workload values all remain LICENSED."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "file": "joulewise/salvage_dangler.py:567",
        "title": "Unbounded recursive walk raises an uncaught RecursionError",
        "scenario": "A valid JSON metadata chain 995 mappings deep reaches _validate_nested_content and raises RecursionError; scripts/run_campaign.py:4822 does not catch it."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "SIX=\"tests.test_run_campaign.D100MembershipRepairTests.test_r8_salvage_runner_appends_new_pinned_row_without_editing_failure tests.test_analysis_integration.AnalysisIntegrationTests.test_b4_salvage_floor_binder_accepts_correct_pair_after_real_row_validation tests.test_whole_window_selection.SalvageSemanticsDispatchTests.test_no_argument_consumers_exclude_salvage_rows tests.test_whole_window_selection.SalvageSemanticsDispatchTests.test_explicit_salvage_dispatch_selects_only_salvage tests.test_whole_window_selection.SalvageSemanticsDispatchTests.test_multiple_salvage_rows_for_one_basis_conflict_even_if_identical tests.test_whole_window_selection.SalvageSemanticsDispatchTests.test_b5_real_row_rejects_same_policy_binding_substitution\"; /Users/edr/code/JouleWise/.venv/bin/python -m unittest $SIX",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "......",
          "Ran 6 tests in 0.619s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 6 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_salvage_dangler tests.test_run_campaign",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 228 tests in 132.814s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 228 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_salvage_dangler.SalvageDanglerTests.test_preworkload_closure_without_quarantine_manifest_refuses tests.test_salvage_dangler.SalvageDanglerTests.test_recursive_metadata_rejects_workload_scalar_in_allowlisted_mapping tests.test_salvage_dangler.SalvageDanglerTests.test_recursive_metadata_rejects_workload_evidence_through_list tests.test_salvage_dangler.SalvageDanglerTests.test_recursive_metadata_admits_producer_owned_extra_scalars",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "....",
          "Ran 4 tests in 0.023s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 4 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python - <<'PY'\nimport json\nfrom tests.test_salvage_dangler import SalvageDanglerTests as T\nfrom joulewise.salvage_dangler import inspect_salvage_attempt as inspect\nt=T(); t.setUp()\nfor name,key,value in [('value','failure','model_output: substituted measured output'),('unicode','ｍｏｄｅｌ＿ｏｕｔｐｕｔ','substituted measured output'),('empty','opaque',{}),('scalar','opaque',0)]:\n p=t.copy_attempt(name); q=p/'metadata.json'; m=json.loads(q.read_text()); m['environment_admission'][key]=value; q.write_text(json.dumps(m,ensure_ascii=False)+'\\n'); print(name,inspect(p)['licensed'])\nt.doCleanups()\nPY",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "value True",
          "unicode True",
          "empty True",
          "scalar True"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "SalvageAuthorizationError"
      }
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python - <<'PY'\nimport json,sys\nfrom tests.test_salvage_dangler import SalvageDanglerTests as T\nfrom joulewise.salvage_dangler import inspect_salvage_attempt\nt=T(); t.setUp(); p=t.copy_attempt(); q=p/'metadata.json'; m=json.loads(q.read_text()); x=0\nfor _ in range(995): x={'opaque':x}\nm['environment_admission']['opaque']=x; sys.setrecursionlimit(10000); q.write_text(json.dumps(m)+'\\n'); sys.setrecursionlimit(1000)\ntry: inspect_salvage_attempt(p)\nexcept BaseException as e: print(type(e).__name__,e)\nt.doCleanups()\nPY",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "RecursionError maximum recursion depth exceeded"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "SalvageAuthorizationError"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --check && git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "DIFF_CHECK_OK",
          "M joulewise/salvage_dangler.py",
          "M tests/test_run_campaign.py",
          "M tests/test_salvage_dangler.py",
          "?? BRIEF.md"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "impl/d100-bii-binding"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The full 2404-test canonical suite was optional and was not rerun by this audit.",
      "needs": "After fixing F1/F2, rerun the focused checks and full canonical suite at the lead gate."
    }
  ]
}
```

## Findings

F1 — blocker: [salvage_dangler.py:526](/private/tmp/claude-501/-Users-edr-code-JouleWise/c701f4e3-95c0-4f1b-a387-854cf845264f/scratchpad/d100bii/joulewise/salvage_dangler.py:526) normalizes keys with only `lower()`, while [salvage_dangler.py:567](/private/tmp/claude-501/-Users-edr-code-JouleWise/c701f4e3-95c0-4f1b-a387-854cf845264f/scratchpad/d100bii/joulewise/salvage_dangler.py:567) traverses scalar leaves without classifying their values. Consequently:

- `environment_admission.failure = "model_output: substituted measured output"` licenses.
- The NFKC-equivalent key `ｍｏｄｅｌ＿ｏｕｔｐｕｔ` licenses.
- Unknown nested `{}` and numeric scalar content licenses.
- Workload bytes placed in both event and summary `failure_reason` license.

Thus the two requested V2 shapes now VOID, but A1 is not closed exactly: workload evidence can still hide in metadata and event-metadata values.

F2 — should_fix: [salvage_dangler.py:567](/private/tmp/claude-501/-Users-edr-code-JouleWise/c701f4e3-95c0-4f1b-a387-854cf845264f/scratchpad/d100bii/joulewise/salvage_dangler.py:567) performs unbounded recursion. Depth 995 raises `RecursionError` from the walk, and [run_campaign.py:4822](/private/tmp/claude-501/-Users-edr-code-JouleWise/c701f4e3-95c0-4f1b-a387-854cf845264f/scratchpad/d100bii/scripts/run_campaign.py:4822) does not catch it. Authorization does not occur, but the inspector’s refusal contract is bypassed by a command-level crash.

Checks performed — CLEAN (A2): replaying the six exact tests against archived `a6ce7af` produced `FAILED (errors=6)`; the identical set against this worktree produced `Ran 6 tests … OK`.

Checks performed — CLEAN (manifest refusal): the new manifest-less test removes `quarantine_manifest` and observes a real `SalvageAuthorizationError`; it is not an assertion-only or mocked refusal.

Checks performed — CLEAN (over-refusal): producer tracing at `controller.py:2243-2254`, `2826-2847`, and `2921-2925` found exactly the six named scalar fields. Null, finite numeric, and literal-`True` constraints match emissions; no seventh runner-owned scalar field was found.

Checks performed — CLEAN (fixture weakening): the shared fixture adds only the quarantine root and canonical per-file manifest. The six consumers retain their original assertions and all pass.

Checks performed — CLEAN (D-106 drift): interval containment, digest freeze, and the in-code D100-BII marker are byte-identical to `a6ce7af`. The three `test_d106_*` methods are also byte-identical.

Checks performed — CLEAN (scope): no repository files were modified by this audit; the declared three-file fix diff and untracked `BRIEF.md` remain unowned.

## Residual risk

The lead should require regressions for scalar-value workload payloads, Unicode-normalized/confusable keys, unknown empty/scalar nested content, and bounded-depth refusal. After those fixes, rerun the six fixture consumers, both focused modules, and the full canonical suite before closing D100-BII-BINDING-01.