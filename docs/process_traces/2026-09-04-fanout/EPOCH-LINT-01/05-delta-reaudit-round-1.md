```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "B2-B5 are cured and B1's wire/overlay mechanics work, but the inline census remains incomplete and historical replay can inspect overlaid rather than committed bytes, so the branch is not landable.",
  "workspace": {
    "base_requested": "18a44de69e398eba40ca8854236f7ec91e10a339",
    "base_mode": "exact",
    "head_start": "18a44de69e398eba40ca8854236f7ec91e10a339",
    "head_end": "18a44de69e398eba40ca8854236f7ec91e10a339",
    "upstream_end": "a6e9edde082f460fbe335d2eac8021f77258b8e6",
    "branch": "feat/2026-09-04-fan-EPOCH-LINT-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/EPOCH-LINT-01/05-delta-reaudit-round-1.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {
        "id": "B1",
        "severity": "blocker",
        "disposition": "NOT CURED",
        "location": "docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md:3574-3584; tests/test_lint_runsheet_epoch.py:380-393",
        "text": "The inline mechanism and authenticated-overlay wire now exist, but the claimed complete census contains only three checks. An existing block names SuccessorPinsetDigestConditionTests under an empty declaration, and a ratification counterfactual adding tests.sample.NoSuchClass under an empty declaration still returns PASS.",
        "counterfactual": "Add a nonexistent unittest class to a declared-empty executable block; ratification must refuse but returned PASS."
      },
      {
        "id": "N1",
        "severity": "blocker",
        "disposition": "NEW",
        "location": "scripts/lint_runsheet_epoch.py:607-608,647-655",
        "text": "patch_overlay is allowed in historical_replay mode, so a self-sealed post-image can replace source from executing_head and turn an absent-at-head symbol into PASS. Historical replay no longer necessarily audits the named Git object.",
        "counterfactual": "Replay an absent symbol with an overlay that adds it; the checker returned PASS with overlay_file_count 1."
      }
    ],
    "refuter_dispositions": [
      {"id": "B1", "result": "NOT CURED", "evidence": "Positive overlay/wire, removal, byte/base, and occupied-root regressions pass and are mutation-biting, but the census-completeness counterfactual passes incorrectly."},
      {"id": "B2", "result": "CURED", "evidence": "Comment-only and echo-only inputs refuse; disabling _check_cli kills the named regression."},
      {"id": "B3", "result": "CURED", "evidence": "HEAD fails the full-lowercase-40-hex rule; bypassing _resolve_commit kills the named regression."},
      {"id": "B4", "result": "CURED", "evidence": "A def-only range below a decorator refuses with definitions span 1-6; disabling the coordinate check kills the named regression."},
      {"id": "B5", "result": "CURED", "evidence": "A module constant resolves; restoring the absent-constant behavior kills the named regression."}
    ],
    "same_signature": "B1 remains open at its census-completeness signature although its wire/overlay subclauses are cured. B2-B5 have no same-signature recurrence. N1 is a distinct new historical-identity defect."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest -v tests.test_lint_runsheet_epoch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 15 tests in 3.683s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 15 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "python3 -c 'import json,subprocess; paths=[\"configs/process/epoch_lint_f0_f3_replay.json\",\"configs/process/epoch_lint_b1_join_replay.json\",\"configs/process/epoch_lint_post_cure_replay.json\"]; rows=[]\nfor p in paths:\n r=subprocess.run([\"python3\",\"scripts/lint_runsheet_epoch.py\",p],capture_output=True,text=True); d=json.loads(r.stdout); rows.append({\"config\":p.split(\"/\")[-1],\"rc\":r.returncode,\"status\":d[\"status\"],\"finding_count\":d[\"finding_count\"],\"kinds\":sorted({x[\"kind\"] for x in d[\"findings\"]})})\nprint(json.dumps(rows,sort_keys=True))'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["[{\"config\": \"epoch_lint_f0_f3_replay.json\", \"finding_count\": 3, \"kinds\": [\"contract_required_cli_inputs\", \"file_line_coordinates\", \"symbol_existence\"], \"rc\": 1, \"status\": \"REFUSE\"}, {\"config\": \"epoch_lint_b1_join_replay.json\", \"finding_count\": 1, \"kinds\": [\"file_line_coordinates\"], \"rc\": 1, \"status\": \"REFUSE\"}, {\"config\": \"epoch_lint_post_cure_replay.json\", \"finding_count\": 0, \"kinds\": [], \"rc\": 0, \"status\": \"PASS\"}]"]},
      "expected": {"exit_code": 0, "tail_regex": "f0_f3.*REFUSE.*b1_join.*REFUSE.*post_cure.*PASS"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "python3 -c 'import json; from tests.test_lint_runsheet_epoch import RunsheetEpochLintTests,_git; from scripts.lint_runsheet_epoch import lint_contract; c=RunsheetEpochLintTests(); c.setUp(); x=c._ratification_contract(); p=c.repo/\"docs/runsheet.md\"; p.write_text(p.read_text()+\"\\n```zsh\\n# joulewise-epoch-lint: {\\\"checks\\\":[]}\\npython -m unittest tests.sample.NoSuchClass\\n```\\n\"); _git(c.repo,\"add\",\"docs/runsheet.md\"); _git(c.repo,\"commit\",\"-qm\",\"undeclared named class\"); x[\"runsheet_revision\"]=_git(c.repo,\"rev-parse\",\"HEAD\"); r=lint_contract(c.repo,x); print(json.dumps({\"check_count\":r[\"check_count\"],\"status\":r[\"status\"],\"undeclared\":\"tests.sample.NoSuchClass\"},sort_keys=True)); c.tearDown()'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["{\"check_count\": 1, \"status\": \"PASS\", \"undeclared\": \"tests.sample.NoSuchClass\"}"]},
      "expected": {"exit_code": 0, "tail_regex": "PASS.*tests.sample.NoSuchClass"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "python3 -c 'import json; from tests.test_lint_runsheet_epoch import RunsheetEpochLintTests; from scripts.lint_runsheet_epoch import lint_contract; c=RunsheetEpochLintTests(); c.setUp(); x=c._ratification_contract(); x[\"mode\"]=\"historical_replay\"; x.pop(\"contract_path\"); x[\"checks\"]=[{\"id\":\"overlay-symbol\",\"kind\":\"symbol_existence\",\"reference\":\"tests/sample.py:test_overlay\",\"reference_occurrences\":2,\"source_path\":\"tests/sample.py\",\"symbol\":\"SampleTests.test_overlay\"}]; r=lint_contract(c.repo,x); print(json.dumps({\"finding_count\":r[\"finding_count\"],\"mode\":r[\"mode\"],\"overlay_file_count\":r[\"overlay_file_count\"],\"status\":r[\"status\"]},sort_keys=True)); c.tearDown()'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["{\"finding_count\": 0, \"mode\": \"historical_replay\", \"overlay_file_count\": 1, \"status\": \"PASS\"}"]},
      "expected": {"exit_code": 0, "tail_regex": "historical_replay.*overlay_file_count.*1.*PASS"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --name-only e0371ab3c823141bf310e8a0fc62191ef40dfac8..HEAD\nstate_delta=$(git diff --name-only e0371ab3c823141bf310e8a0fc62191ef40dfac8..HEAD -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json docs/decision_log.md PROJECT_STATUS.md)\ntest -z \"$state_delta\"\nprintf 'MAGISTRATE_STATE_DELTA=none\\n'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["tests/test_lint_runsheet_epoch.py", "MAGISTRATE_STATE_DELTA=none"]},
      "expected": {"exit_code": 0, "tail_regex": "tests/test_lint_runsheet_epoch.py.*MAGISTRATE_STATE_DELTA=none"}
    }
  ],
  "flags": []
}
```

## Findings

1. **B1 — blocker — NOT CURED.** The ruled overlay and ratification wire now bite: the positive path passes, removing a declaration/wire refuses, byte/base changes refuse, and an occupied overlay root refuses. The census itself is not complete. It has only three checks, while the executable block at lines 3574–3584 names `SuccessorPinsetDigestConditionTests` under `{"checks":[]}`. More decisively, a focused ratification with a new empty-declared block naming nonexistent `tests.sample.NoSuchClass` returned `PASS`. This is the same census-completeness signature as B1, not a new acceptance interpretation.

2. **N1 — blocker — NEW.** Historical replay accepts `patch_overlay`. A focused replay named an exact executing commit where `SampleTests.test_overlay` was absent, supplied a self-sealed overlay adding it, and returned `PASS` with one overlay file. That defeats the mission's executing-head identity rule and can make the motivating historical replays inspect substituted bytes. Restrict overlay support to ratification mode and add a refusal regression.

B2, B3, B4, and B5 are **CURED**. Their named regressions passed, and a counterfactual mutation of each production seam killed its regression. The historical F0–F3 and B1 replays still refuse with the expected signatures, and the post-cure replay passes. The fix-round diff changes no magistrate-owned state document.

## Residual risk

Per preflight, only the touched test module was run; the repository-wide suite was intentionally not run. No additional coverage limitation changes the verdict.
