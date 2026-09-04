```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "The refreshed mission-only delta is scope-clean, its focused test and claimed probe pass, and three assertion-specific mutations confirm the documentation guard is counterfactual; the delta is LANDABLE.",
  "workspace": {
    "base_requested": "git merge-base origin/main HEAD = b0ed6991c11f3a515ad293760c6dfc031adda8e1",
    "base_mode": "exact",
    "head_start": "c3cd13c22fe77c5cbd5e02ae7c2277b4e6f50aea",
    "head_end": "c3cd13c22fe77c5cbd5e02ae7c2277b4e6f50aea",
    "upstream_end": "ec8f780337326f82feb1848a972c4746612da6cc",
    "branch": "feat/2026-09-04-fan-MIDCAMPAIGN-CURE-GENERATION-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/MIDCAMPAIGN-CURE-GENERATION-01/02-refuter-merge-base.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "LANDABLE",
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "base=$(git merge-base origin/main HEAD); git diff --name-status \"$base\"..HEAD; git diff --exit-code \"$base\"..HEAD -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json docs/decision_log.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "M docs/process_traces/2026-08-22-t20/real-transaction-runbook.md",
          "A docs/process_traces/2026-09-04-fanout/MIDCAMPAIGN-CURE-GENERATION-01/01-sol-report.md",
          "A tests/test_midcampaign_cure_generation_docs.py",
          "state-file diff produced no output"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "M\\s+docs/process_traces/2026-08-22-t20/real-transaction-runbook\\.md[\\s\\S]*A\\s+tests/test_midcampaign_cure_generation_docs\\.py"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest -v tests.test_midcampaign_cure_generation_docs",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 2 tests in 0.000s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 - <<'PY'\nfrom pathlib import Path\nimport os, subprocess, sys, tempfile\nsource = Path('docs/process_traces/2026-08-22-t20/real-transaction-runbook.md').read_text(encoding='utf-8')\nstart = source.index('### The mid-campaign cure boundary (D-153 W5)')\nend = source.index(\"**H1's continuation clause\", start)\nwith tempfile.TemporaryDirectory(prefix='midcampaign-cure-mutant-') as directory:\n    path = Path(directory) / 'real-transaction-runbook.md'\n    path.write_text(source[:start] + source[end:], encoding='utf-8')\n    env = os.environ.copy(); env['MIDCAMPAIGN_CURE_TRANSACTION_RECORD'] = str(path)\n    run = subprocess.run([sys.executable, '-m', 'unittest', 'tests.test_midcampaign_cure_generation_docs'], env=env, text=True, capture_output=True)\n    if run.returncode == 0: raise SystemExit('counterfactual unexpectedly passed')\n    print(f'MUTANT_EXIT={run.returncode}')\n    print('COUNTERFACTUAL_PASS: removing the D-153 section makes the focused module fail')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "MUTANT_EXIT=1",
          "COUNTERFACTUAL_PASS: removing the D-153 section makes the focused module fail"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "MUTANT_EXIT=1\\nCOUNTERFACTUAL_PASS: removing the D-153 section makes the focused module fail"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 - <<'PY'\nfrom pathlib import Path\nimport os, subprocess, sys, tempfile\nsource = Path('docs/process_traces/2026-08-22-t20/real-transaction-runbook.md').read_text(encoding='utf-8')\nmutations = [('definition_boundary','configuration choice that the frozen plan already permits','configuration setting selected after the plan freezes','test_transaction_record_defines_the_non_configuration_boundary','configuration choice that the frozen plan already permits'),('new_generation_consequence','A new family generation is required','The existing family generation may continue','test_every_registered_profile_requires_a_new_generation','A new family generation is required'),('all_profile_scope','ALPHA, BETA, and GAMMA','ALPHA and BETA','test_every_registered_profile_requires_a_new_generation',\"'GAMMA' not found\")]\nwith tempfile.TemporaryDirectory(prefix='midcampaign-refuter-') as directory:\n    for name, old, new, method, evidence in mutations:\n        assert source.count(old) == 1\n        path = Path(directory) / f'{name}.md'; path.write_text(source.replace(old, new, 1), encoding='utf-8')\n        env = os.environ.copy(); env['MIDCAMPAIGN_CURE_TRANSACTION_RECORD'] = str(path)\n        test = f'tests.test_midcampaign_cure_generation_docs.MidcampaignCureGenerationDocsTests.{method}'\n        run = subprocess.run([sys.executable, '-m', 'unittest', '-v', test], env=env, text=True, capture_output=True)\n        assert run.returncode != 0 and evidence in run.stdout + run.stderr\n        print(f'{name}: EXPECTED_FAIL rc={run.returncode} evidence={evidence}')\nprint('COUNTERFACTUALS_OK=3')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "definition_boundary: EXPECTED_FAIL rc=1 evidence=configuration choice that the frozen plan already permits",
          "new_generation_consequence: EXPECTED_FAIL rc=1 evidence=A new family generation is required",
          "all_profile_scope: EXPECTED_FAIL rc=1 evidence='GAMMA' not found",
          "COUNTERFACTUALS_OK=3"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "definition_boundary: EXPECTED_FAIL[\\s\\S]*new_generation_consequence: EXPECTED_FAIL[\\s\\S]*all_profile_scope: EXPECTED_FAIL[\\s\\S]*COUNTERFACTUALS_OK=3"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "base=$(git merge-base origin/main HEAD); git diff --check \"$base\"..HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "no output"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "The paper-facing acceptance half is intentionally absent from this delta; the 2026-09-04 magistrate ruling assigns the proposed Further limitations paragraph to the paper lane after paper-e/f/g merge.",
      "needs": "Paper-lane owner carries the ruled paragraph after paper-e/f/g merge."
    }
  ]
}
```

## Findings

None. The mission-only delta is **LANDABLE**.

## Evidence

- **Scope:** `git diff $(git merge-base origin/main HEAD)..HEAD` contains exactly the three paths listed by `01-sol-report.md` as its scope of record. `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`, and `docs/decision_log.md` have no delta.
- **Claimed checks:** the focused module passes 2/2. The implementer's exact section-removal probe returns mutant exit 1 as claimed. The paper-absence inspection also returns the claimed result; under the later magistrate ruling, that absence is assigned to the paper lane and does not block this landing.
- **Behavioural counterfactuals:** changing the permitted-choice boundary makes `test_transaction_record_defines_the_non_configuration_boundary` fail; changing “new family generation is required” to continuation permission makes `test_every_registered_profile_requires_a_new_generation` fail; removing GAMMA from the all-profile clause makes that same test fail on the missing profile. All mutations were made only in temporary copies.
- **Previous-round blocker replay:** no previous refuter verdict is present in this mission directory or reachable history, so there is no recorded non-staleness blocker to replay. The potentially applicable false-counterfactual class is closed by V4's assertion-specific failures. Spoofable CLI checks, trusted mutable identifiers, and occupied-root admission are not applicable to this documentation-only delta.
- **Preflight compliance:** only `tests.test_midcampaign_cure_generation_docs`, the sole touched test module, was run; the whole suite was not run.

## Residual risk

The reader-facing paper paragraph remains future work under the explicit magistrate routing. This is not evidence that the paper acceptance half has already landed and is not a blocker to this mission delta.
