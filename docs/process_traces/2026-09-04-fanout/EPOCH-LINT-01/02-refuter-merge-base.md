```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The refreshed mission-only delta is in scope and its focused tests pass, but five execution blockers make EPOCH-LINT-01 not landable.",
  "workspace": {
    "base_requested": "590a6d7eab206daaf824f9eed1df26638bc1d7e0",
    "base_mode": "exact",
    "head_start": "590a6d7eab206daaf824f9eed1df26638bc1d7e0",
    "head_end": "590a6d7eab206daaf824f9eed1df26638bc1d7e0",
    "upstream_end": "b0ed6991c11f3a515ad293760c6dfc031adda8e1",
    "branch": "feat/2026-09-04-fan-EPOCH-LINT-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/EPOCH-LINT-01/02-refuter-merge-base.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {
        "id": "B1",
        "severity": "blocker",
        "location": "01-magistrate-rulings.md:11; 01-sol-report.md:143-162; lint_runsheet_epoch.py:315-349",
        "text": "The ruled inline census and authenticated overlay are absent, as are the required ratification wire and clean transcript.",
        "counterfactual": "Removing a declaration or changing an overlay byte/base must refuse; no such path exists to test."
      },
      {
        "id": "B2",
        "severity": "blocker",
        "location": "scripts/lint_runsheet_epoch.py:191-261",
        "text": "Substring CLI validation accepts flags in comments and command text in echo output as real invocations.",
        "counterfactual": "Comment-only and echo-only authenticator inputs must REFUSE; both probes passed."
      },
      {
        "id": "B3",
        "severity": "blocker",
        "location": "scripts/lint_runsheet_epoch.py:55-59",
        "text": "Mutable revisions such as HEAD are accepted as contract identities.",
        "counterfactual": "HEAD must fail closed; it instead resolved 590a6d7e."
      },
      {
        "id": "B4",
        "severity": "blocker",
        "location": "scripts/lint_runsheet_epoch.py:290-304",
        "text": "AST node.lineno excludes decorators, so a purported whole-symbol range can omit them.",
        "counterfactual": "A range starting at the def below @d must REFUSE; it passed."
      },
      {
        "id": "B5",
        "severity": "blocker",
        "location": "scripts/lint_runsheet_epoch.py:78-103",
        "text": "Discovery omits constants, although the mission explicitly requires them.",
        "counterfactual": "`TOKEN = 1` checked as TOKEN must pass; it was reported absent."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest -v tests.test_lint_runsheet_epoch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 6 tests in 2.834s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 6 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "out=$(mktemp); python3 scripts/lint_runsheet_epoch.py configs/process/epoch_lint_f0_f3_replay.json > \"$out\"; rc=$?; jq -c '{status,finding_count,kinds:[.findings[].kind]}' \"$out\"; test \"$rc\" -eq 1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["{\"status\":\"REFUSE\",\"finding_count\":3,\"kinds\":[\"symbol_existence\",\"contract_required_cli_inputs\",\"file_line_coordinates\"]}"]},
      "expected": {"exit_code": 0, "tail_regex": "REFUSE.*finding_count.*3"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "out=$(mktemp); python3 scripts/lint_runsheet_epoch.py configs/process/epoch_lint_b1_join_replay.json > \"$out\"; rc=$?; jq -c '{status,finding_count,detail:.findings[0].detail}' \"$out\"; test \"$rc\" -eq 1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["{\"status\":\"REFUSE\",\"finding_count\":1,\"detail\":\"cites scripts/generate_arm_readiness.py:28-186; definitions span 28-192\"}"]},
      "expected": {"exit_code": 0, "tail_regex": "REFUSE.*28-186.*28-192"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "python3 scripts/lint_runsheet_epoch.py configs/process/epoch_lint_post_cure_replay.json | jq -c '{status,finding_count,check_count}'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["{\"status\":\"PASS\",\"finding_count\":0,\"check_count\":3}"]},
      "expected": {"exit_code": 0, "tail_regex": "PASS.*finding_count.*0.*check_count.*3"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "base=$(git merge-base origin/main HEAD); git diff --name-only \"$base\"..HEAD; git diff --name-only \"$base\"..HEAD -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json docs/decision_log.md",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["tests/test_lint_runsheet_epoch.py"]},
      "expected": {"exit_code": 0, "tail_regex": "tests/test_lint_runsheet_epoch.py"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "python3 - <<'PY'\nfrom unittest.mock import patch\nfrom tests.test_lint_runsheet_epoch import RunsheetEpochLintTests\nfor name in ('_check_symbol','_check_cli','_check_coordinates'):\n c=RunsheetEpochLintTests(methodName='test_counterfactual_pre_cure_shape_reports_all_three_kinds'); c.setUp()\n try:\n  with patch('scripts.lint_runsheet_epoch.'+name,return_value=[]):\n   try: c.test_counterfactual_pre_cure_shape_reports_all_three_kinds()\n   except AssertionError: print(name+': KILLED')\n   else: raise SystemExit(name+': SURVIVED')\n finally: c.tearDown()\nPY",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["_check_symbol: KILLED", "_check_cli: KILLED", "_check_coordinates: KILLED"]},
      "expected": {"exit_code": 0, "tail_regex": "_check_symbol: KILLED.*_check_cli: KILLED.*_check_coordinates: KILLED"}
    },
    {
      "id": "V7",
      "kind": "other",
      "cmd": "python3 -c 'from pathlib import Path; import scripts.lint_runsheet_epoch as m; c={\"id\":\"i\",\"kind\":\"contract_required_cli_inputs\",\"block_anchor\":\"a\",\"command\":\"c\",\"required_flags\":[\"--x\"]}; p=lambda s:not m._check_cli(\"```zsh\\na \"+s+\"\\n```\",c); print(\"comment=\"+str(p(\"c # --x\"))); print(\"echo=\"+str(p(\"echo c --x\"))); print(\"mutable=\"+m._resolve_commit(Path(\".\"),\"HEAD\",\"r\")[:8]); m._git_text=lambda *a:\"@d\\ndef f():\\n pass\\n\"; q={\"id\":\"i\",\"kind\":\"file_line_coordinates\",\"reference\":\"x:2-3\",\"source_path\":\"x\",\"start_symbol\":\"f\",\"end_symbol\":\"f\",\"cited_start\":2,\"cited_end\":3}; print(\"decorator=\"+str(not m._check_coordinates(Path(\".\"),\"h\",\"x:2-3\",q,{}))); print(\"constant=\"+str(m._resolve_definition(\"X=1\\n\",\"x\",\"X\")[1]))'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["comment=True", "echo=True", "mutable=590a6d7e", "decorator=True", "constant=symbol 'X' is absent from x"]},
      "expected": {"exit_code": 0, "tail_regex": "comment=True.*echo=True.*mutable=590a6d7e.*decorator=True.*constant=symbol"}
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "git diff --check && base=$(git merge-base origin/main HEAD) && git diff --check \"$base\"..HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "blocking",
      "text": "No prior verdict file exists at this head. CLI spoofing and mutable identity are open; occupied-root handling is absent with the overlay; V6 closes false-counterfactual risk.",
      "needs": "Resume implementation under the issued ruling, cure B1-B5, and rerun the focused gauntlet."
    }
  ]
}
```

## Findings

1. **B1 — blocker:** The issued inline-census and authenticated-overlay ruling has not been implemented, and the required ratification wire/transcript is absent.
2. **B2 — blocker:** Comment and echo text can spoof a CLI invocation and its required authenticator inputs.
3. **B3 — blocker:** Mutable revision expressions are accepted as contract identities.
4. **B4 — blocker:** Decorated definitions can be cited without their decorators and still pass.
5. **B5 — blocker:** Constants required by the mission are not discoverable.

## Evidence

The mission-only range is `git diff $(git merge-base origin/main HEAD)..HEAD`. It contains exactly the six paths declared by the seat report: three replay JSON files, the seat report, the checker, and its focused test module. `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`, and `docs/decision_log.md` have no delta in that range.

All claimed focused checks passed: six unit tests, the three-kind fixation replay, the B1 join-drift replay, and the post-cure replay. The whole suite was not run, per preflight. V6 independently establishes the counterfactual for each implemented behavior: disabling the symbol, CLI, or coordinate finding with a one-line mutation in an isolated temporary copy makes `test_counterfactual_pre_cure_shape_reports_all_three_kinds` fail.

The adversarial V7 probes establish the blockers directly. The CLI checker accepts both a required flag present only in an inline comment and an echo line that merely contains the target command text. `HEAD` is accepted as a revision. A range starting on a decorated function's `def` line is accepted despite omitting the decorator. A real module constant is reported absent.

Previous-round status: no prior refuter verdict file is present in this directory at the reviewed head. Of the explicitly requested non-staleness examples, spoofable CLI checking and trusted mutable identity are open; occupied-root refusal is not implemented because the overlay itself is absent; false-counterfactual concern is closed by the three mutation kills.

## Residual risk

No additional coverage limitation changes the verdict. The branch needs a resumed implementation and another focused refuter pass after B1-B5 are cured.
