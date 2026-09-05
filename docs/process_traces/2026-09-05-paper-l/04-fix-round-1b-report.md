```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "D3 implemented: pinned appendix DERIVE rows are checked and refused as Results fills.",
  "workspace": {
    "base_requested": "7bbf020e",
    "base_mode": "exact",
    "head_start": "7bbf020e3e01d626e6be8cd2b2e3d5688a3df07e",
    "head_end": "7bbf020e3e01d626e6be8cd2b2e3d5688a3df07e",
    "upstream_end": "7bbf020e3e01d626e6be8cd2b2e3d5688a3df07e",
    "branch": "feat/2026-09-05-paper-l"
  },
  "pathspec": [
    "scripts/render_results_fills.py",
    "scripts/check_paper_round7_artifacts.py",
    "tests/test_render_results_fills.py",
    "tests/test_paper_round7_artifacts.py",
    "docs/process_traces/2026-09-05-paper-l/04-fix-round-1b-report.md"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_render_results_fills -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 29 tests in 1.523s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 29 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_terms_lint -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 5 tests in 1.389s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 5 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_round7_artifacts -v",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: 187 != 184",
          "",
          "----------------------------------------------------------------------",
          "Ran 59 tests in 609.767s",
          "",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 - <<'PY'\nfrom pathlib import Path\nimport subprocess\nimport sys\nchecker = Path(\"scripts/check_paper_round7_artifacts.py\")\nrenderer = Path(\"scripts/render_results_fills.py\")\ncases = [\n    (\"checker producer pins\", checker,\n     \"for row in spec.rows.values() if isinstance(row, AppendixDeriveRow)\",\n     \"for row in () if isinstance(row, AppendixDeriveRow)\",\n     \"tests.test_paper_round7_artifacts.AppendixDeriveProductionTests.test_checker_cli_refuses_producer_digest_and_size_drift\"),\n    (\"checker placement\", checker,\n     \"comparisons.extend(check_appendix_placement(skeleton_text, spec))\",\n     \"pass  # MUTANT: omit appendix placement\",\n     \"tests.test_paper_round7_artifacts.AppendixDeriveProductionTests.test_checker_cli_refuses_missing_duplicate_or_moved_marker\"),\n    (\"renderer registry recognition\", renderer,\n     'and cells[4] == \"DERIVE\":',\n     'and cells[4] == \"DISABLED\":',\n     \"tests.test_render_results_fills.AppendixDeriveProductionTests.test_production_renderer_knows_pe01_and_refuses_results_prose\"),\n    (\"renderer substitution refusal\", renderer,\n     \"    _refuse_appendix_derivations(text)\\n    seen: set[str] = set()\",\n     \"    seen: set[str] = set()\",\n     \"tests.test_render_results_fills.AppendixDeriveProductionTests.test_production_renderer_knows_pe01_and_refuses_results_prose\"),\n]\nfor label, path, old, new, test in cases:\n    original = path.read_bytes()\n    source = original.decode(\"utf-8\")\n    assert source.count(old) == 1, label\n    try:\n        path.write_text(source.replace(old, new, 1), encoding=\"utf-8\")\n        result = subprocess.run([sys.executable, \"-m\", \"unittest\", test, \"-v\"],\n                                text=True, capture_output=True)\n    finally:\n        path.write_bytes(original)\n    output = result.stdout + result.stderr\n    assert result.returncode == 1 and \"FAILED (failures=\" in output, output\n    print(label + \": exit 1; \" + output.strip().splitlines()[-1])\nprint(\"4/4 production mutations killed; source bytes restored\")\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "checker producer pins: exit 1; FAILED (failures=2)",
          "checker placement: exit 1; FAILED (failures=3)",
          "renderer registry recognition: exit 1; FAILED (failures=1)",
          "renderer substitution refusal: exit 1; FAILED (failures=1, errors=1)",
          "4/4 production mutations killed; source bytes restored"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "4/4 production mutations killed; source bytes restored"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_round7_artifacts -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 59 tests in 607.857s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 59 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": []
}
```

## Change

D3 is implemented. The checker includes PE-01 and future seven-column appendix DERIVE rows in its parsed registry, binds each producer's SHA-256 and byte size to the script on disk, and requires exactly one marker in the appendix section named by the row. Legacy DX rendering and its 16-row placement census remain unchanged.

The Results renderer loads the column-two appendix marker as a known VALUE_UNISSUED row. It refuses these markers both before token substitution and during final-output validation, including an attempted supplied numeric fill. New renderer regressions import production without the existing tests' frozen pre-v5 registry overrides. Future-row controls use ZZ-42; the checker also accepts an Appendix B.2 placement.

D3 clause map (line numbers on this working tree):

| Production site | Biting regression | Executed counterfactual |
|---|---|---|
| scripts/check_paper_round7_artifacts.py:412, producer pins | test_paper_round7_artifacts.py:187, test_checker_cli_refuses_producer_digest_and_size_drift | Omit appendix producer pins from file checks: two failures. |
| scripts/check_paper_round7_artifacts.py:962, placement integration | test_paper_round7_artifacts.py:203, test_checker_cli_refuses_missing_duplicate_or_moved_marker | Omit appendix placement comparisons: three failures. |
| render_results_fills.py:100, registry loading | test_render_results_fills.py:218, test_production_renderer_knows_pe01_and_refuses_results_prose | Disable recognition of DERIVE: known-row assertion fails. |
| render_results_fills.py:830, substitution guard | test_render_results_fills.py:218, same regression | Remove appendix refusal before substitution: the no-fill case fails and the supplied-fill case raises the wrong exception. |

Next exact step: the lead reviews this D3 diff and the report. No commit was made.

## Verification notes

The first checker run completed all three byte-identical producer/artifact replays but failed its final total-count assertion: 187 observed versus the already-loaded 184 expectation. The count was corrected to 187 (184 digest/placement comparisons plus three replay comparisons); the fresh full-module run is recorded separately.

Mutation failures are intentional and required. Every mutant was applied to an authorized production file, tested serially, and restored byte-for-byte in a finally block. The mutation command in the envelope is directly replayable from this checkout and must run with no concurrent writer.

M0 found no active stop card and a clean workspace at the exact requested base. Only the three authorized test modules were run, one at a time, with the required corpus root. No discovery suite, agent launch, measurement, or commit occurred. A read-only process-list attempt was sandbox-denied; verification continued through the test log without escalation.

