```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Cured B2-B5 and implemented the ruled inline-census/authenticated-overlay machinery for B1; installing the complete S-0 census and actual ratification wire needs the runsheet added to WRITE_SCOPE.",
  "workspace": {
    "base_requested": "590a6d7eab206daaf824f9eed1df26638bc1d7e0",
    "base_mode": "exact",
    "head_start": "590a6d7eab206daaf824f9eed1df26638bc1d7e0",
    "head_end": "590a6d7eab206daaf824f9eed1df26638bc1d7e0",
    "upstream_end": "590a6d7eab206daaf824f9eed1df26638bc1d7e0",
    "branch": "feat/2026-09-04-fan-EPOCH-LINT-01"
  },
  "pathspec": [
    "configs/process/epoch_lint_b1_join_replay.json",
    "configs/process/epoch_lint_f0_f3_replay.json",
    "configs/process/epoch_lint_post_cure_replay.json",
    "docs/process_traces/2026-09-04-fanout/EPOCH-LINT-01/03-sol-fix-round-1-report.md",
    "scripts/lint_runsheet_epoch.py",
    "tests/test_lint_runsheet_epoch.py"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-fanout/EPOCH-LINT-01/02-refuter-merge-base.md"
  ],
  "verdict": {
    "implementation": "partial",
    "acceptance": "pending_verification"
  },
  "scope_expansion": {
    "requested_paths": [
      "docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md"
    ],
    "reason": "The adopted inline-declaration ruling and B1 require the complete S-0 obligation census plus its ratification command to live in the runsheet; that existing path is outside the exhaustive allowlist.",
    "blocked_work": "Install declarations for every executable block and cited mechanics group, wire the exact epoch-lint invocation into section 0.1, then run and retain the clean named-revision transcript.",
    "minimal_change": "Add only the inline declaration census and ratification invocation to the existing S-0 runsheet; use the already-authorized checker, config, test, and trace paths for all other work."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "zsh -o pipefail -c 'python3 -m unittest -v tests.test_lint_runsheet_epoch 2>&1 | tail -n 1'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "^OK$"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "zsh -c 'out=$(mktemp); python3 scripts/lint_runsheet_epoch.py configs/process/epoch_lint_f0_f3_replay.json > \"$out\"; rc=$?; jq -c \"{status,mode,finding_count,kinds:[.findings[].kind]}\" \"$out\"; test \"$rc\" -eq 1'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["{\"status\":\"REFUSE\",\"mode\":\"historical_replay\",\"finding_count\":3,\"kinds\":[\"symbol_existence\",\"contract_required_cli_inputs\",\"file_line_coordinates\"]}"]},
      "expected": {"exit_code": 0, "tail_regex": "REFUSE.*historical_replay.*finding_count.*3"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "zsh -c 'out=$(mktemp); python3 scripts/lint_runsheet_epoch.py configs/process/epoch_lint_b1_join_replay.json > \"$out\"; rc=$?; jq -c \"{status,mode,finding_count,detail:.findings[0].detail}\" \"$out\"; test \"$rc\" -eq 1'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["{\"status\":\"REFUSE\",\"mode\":\"historical_replay\",\"finding_count\":1,\"detail\":\"cites scripts/generate_arm_readiness.py:28-186; definitions span 28-192\"}"]},
      "expected": {"exit_code": 0, "tail_regex": "REFUSE.*28-186.*28-192"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "python3 scripts/lint_runsheet_epoch.py configs/process/epoch_lint_post_cure_replay.json | jq -c '{status,mode,finding_count,check_count}'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["{\"status\":\"PASS\",\"mode\":\"historical_replay\",\"finding_count\":0,\"check_count\":3}"]},
      "expected": {"exit_code": 0, "tail_regex": "PASS.*finding_count.*0.*check_count.*3"}
    },
    {
      "id": "V5",
      "kind": "lint",
      "cmd": "python3 -m py_compile scripts/lint_runsheet_epoch.py tests/test_lint_runsheet_epoch.py && git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "python3 - <<'PY'\nfrom unittest.mock import patch\nfrom tests.test_lint_runsheet_epoch import RunsheetEpochLintTests\nfor name in ('_check_symbol','_check_cli','_check_coordinates'):\n c=RunsheetEpochLintTests(methodName='test_counterfactual_pre_cure_shape_reports_all_three_kinds'); c.setUp()\n try:\n  with patch('scripts.lint_runsheet_epoch.'+name,return_value=[]):\n   try: c.test_counterfactual_pre_cure_shape_reports_all_three_kinds()\n   except AssertionError: print(name+': KILLED')\n   else: raise SystemExit(name+': SURVIVED')\n finally: c.tearDown()\nPY",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["_check_symbol: KILLED", "_check_cli: KILLED", "_check_coordinates: KILLED"]},
      "expected": {"exit_code": 0, "tail_regex": "_check_symbol: KILLED.*_check_cli: KILLED.*_check_coordinates: KILLED"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "B1's checker and regressions are implemented, but the complete inline census and live runsheet-revision wire cannot be installed in the out-of-scope S-0 runsheet.",
      "needs": "Resume with docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md added to WRITE_SCOPE."
    }
  ]
}
```

## Change

B2 now tokenizes the anchored logical invocation, strips shell comments, and requires the declared command prefix, so comment-only flags and echo-only command text refuse. B3 accepts only an exact full lowercase commit object ID. B4 includes decorator lines in whole-symbol coordinates. B5 discovers module and class constants through AST assignments.

B1 now has an explicit ratification mode: every column-zero executable zsh block must begin with an inline JSON declaration, the runsheet must invoke its exact epoch-lint contract once, and checks may read authenticated post-image overlay bytes whose manifest, base commit, base bytes, and result bytes are all digest-bound. Overlay staging refuses an occupied root. Historical examples are explicitly marked `historical_replay` and retain both motivating refusal shapes plus the clean post-cure replay.

| Finding | Cure | File:line |
|---|---|---|
| B1 | Inline declaration census, exact self-ratification invocation, named-base authenticated overlay, occupied-root refusal | `scripts/lint_runsheet_epoch.py:420`, `scripts/lint_runsheet_epoch.py:561`, `tests/test_lint_runsheet_epoch.py:341` |
| B2 | Tokenized anchor/command prefix and exact option tokens; comment and echo counterfactuals | `scripts/lint_runsheet_epoch.py:281`, `tests/test_lint_runsheet_epoch.py:202` |
| B3 | Full lowercase 40-hex exact-commit identity | `scripts/lint_runsheet_epoch.py:71`, `tests/test_lint_runsheet_epoch.py:239` |
| B4 | Decorator-aware definition start | `scripts/lint_runsheet_epoch.py:385`, `tests/test_lint_runsheet_epoch.py:244` |
| B5 | Module/class `Assign` and `AnnAssign` discovery | `scripts/lint_runsheet_epoch.py:91`, `tests/test_lint_runsheet_epoch.py:269` |

No magistrate-owned state row should change yet. After the resumed run installs the complete S-0 census and banks the clean named-revision transcript, the magistrate can retire `EPOCH-LINT-01`; until then its current queued row remains exact.

## Verification notes

The repository-wide suite was not run, per the explicit preflight rule. `rg` found no other Python module importing the changed checker, so only `tests.test_lint_runsheet_epoch`, the three replay commands, compile/diff checks, and the prior mutation-kill probe were run.

## Residual risk

The ratification mechanism is covered, but the actual S-0 runsheet still has no complete inline obligation census or ratification command. That is the sole blocking residue and the reason for the narrow scope request above.
