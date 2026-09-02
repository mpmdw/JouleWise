```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "One should-fix: the new unavailable-corpus docstring promises a resolved path even though both producer exit-3 branches emit a flattened producer message.",
  "workspace": {
    "base_requested": "73f7fcc2",
    "base_mode": "exact",
    "head_start": "7fc87a7fae9a836f87e38c8a8e89d8c642dd06d5",
    "head_end": "7fc87a7fae9a836f87e38c8a8e89d8c642dd06d5",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "SF2-CONTRACT",
        "severity": "should_fix",
        "location": "scripts/check_paper_round7_artifacts.py:16,23-26,837-841,900-902,929-930",
        "summary": "The documented `<resolved path>` grammar is false for producer-return-code-3 failures.",
        "evidence": "The committed multiline regression and an independent AS-branch probe both emit flattened producer text after `R7F CORPUS UNAVAILABLE: `, not a path."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=\"$TMPDIR\" python3 -m unittest -q tests.test_paper_round7_artifacts.RegistryAndDigestTests tests.test_paper_round7_artifacts.RefusalTests tests.test_paper_round7_artifacts.TypedArtifactCliTests tests.test_paper_round7_artifacts.InvocationTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 44 tests in 2.527s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 44 tests in [0-9.]+s\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=\"$TMPDIR\" python3 scripts/check_paper_round7_artifacts.py --literals-only",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "R7F PLACED 0/16",
          "R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "R7F PLACED 0/16\\nR7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=\"$TMPDIR\" R7F_CORPUS_ROOT=\"$TMPDIR/r7f-audit-absent-corpus\" python3 -m unittest -q tests.test_paper_round7_artifacts",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 45 tests in 2.543s",
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 45 tests in [0-9.]+s\\nOK \\(skipped=1\\)"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=\"$TMPDIR\" python3 -m unittest -q tests.test_paper_round7_artifacts.TypedArtifactCliTests.test_multiline_producer_unavailable_is_flattened_to_last_line",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 0.001s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test in [0-9.]+s\\nOK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The retained-corpus live replay was not rerun during this audit; the delta does not alter its successful producer path.",
      "needs": ""
    }
  ]
}
```

VERDICT: SHOULD-FIX 1

## Findings

- **SF2-CONTRACT — should-fix**  
  [scripts/check_paper_round7_artifacts.py:16](/Users/edr/code/JouleWise-wt-dx2/scripts/check_paper_round7_artifacts.py:16) and [line 23](/Users/edr/code/JouleWise-wt-dx2/scripts/check_paper_round7_artifacts.py:23) promise `<resolved path>` for an unavailable corpus. But both exit-3 sites call the helper at [line 837](/Users/edr/code/JouleWise-wt-dx2/scripts/check_paper_round7_artifacts.py:837), which emits flattened producer output. The committed test’s stub demonstrates the non-path form, and an independent AS-path probe produced `R7F CORPUS UNAVAILABLE: AS first line | AS second line`. Clarify the contract to distinguish preflight missing paths from producer exit-3 messages, or make code always emit a path.

Contract arithmetic is otherwise correct: 181 base comparisons, one per literal occurrence, plus exactly three replay byte comparisons (XD, F4, AQ). A correct one-per-row 16-marker synthetic placement yields 197 literals-only and 200 full replay; the current zero-placement tail is 181/184. The checklist states this accurately.

The committed regression directly reaches XS only, because its first mocked producer exits 3. This is sufficient for the accepted shared-helper design: both XS and AS invoke the same helper, and the AS dynamic probe confirmed the identical flattened last-line behavior. Single-line producer output is byte-identical before and after (`R7F CORPUS UNAVAILABLE: single producer message\n`).

`R7F_CORPUS_ROOT` does not redirect `ROOT` or `REGISTRY_PATH`: `ROOT` remains test-file-relative; the registry override is independent; the corpus override reaches only replay. The override run correctly skipped the replay class.

Scope is clean: all eight changed paths are the two seat files, checklist, or dx-registry custody files; `git diff --check` and workspace status are clean.

## Residual risk

The full retained-corpus replay was not repeated in this audit.