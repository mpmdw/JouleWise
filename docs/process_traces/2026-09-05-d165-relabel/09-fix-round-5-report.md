```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "A and B fixed: exact reasoned census GREEN; producer-declared replay era enforced with named refusal and eight-case mutation kill.",
  "workspace": {
    "base_requested": "d4265ad7",
    "base_mode": "exact",
    "head_start": "d4265ad7a26184b5fedfedc3f4978a9fca399059",
    "head_end": "d4265ad7a26184b5fedfedc3f4978a9fca399059",
    "upstream_end": "d4265ad7a26184b5fedfedc3f4978a9fca399059",
    "branch": "feat/2026-09-05-d165-relabel"
  },
  "pathspec": [
    "joulewise/dominance_closeout.py",
    "tests/test_d165_dominance_closeout.py",
    "tests/test_d165_rationale_census.py",
    "tests/fixtures/d165_rationale_allowlist.json",
    "docs/contracts/d165_dominance_closeout.md",
    "docs/process_traces/2026-09-05-d165-relabel/09-fix-round-5-report.md"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d165_rationale_census",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: False is not true : Required legacy allowlist missing: tests/fixtures/d165_rationale_legacy_allowlist.json",
          "Ran 4 tests in 3.263s",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d165_dominance_closeout",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 51 tests in 11.271s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d165_dominance_closeout",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: 'cff755ba28175cff51bc47298ee97c97011444c8a7f2dd08de89d3216fe38500' != 'f0f8e86e2aa6c9a3c920e026813b8ce9c34c78e5b21dc7457cbe7bf2de9ba870'",
          "Ran 55 tests in 11.208s",
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nimport ast\nimport inspect\nimport unittest\nfrom unittest import mock\nfrom joulewise import dominance_closeout as core\nsource = inspect.getsource(core._validate_common_mode_result)\ntree = ast.parse(source)\nchanged = 0\nfor node in ast.walk(tree):\n    if isinstance(node, ast.If) and ast.unparse(node.test) == 'rule_id != sidecar_rule_id':\n        node.test = ast.Constant(value=False)\n        changed += 1\nassert changed == 1, changed\nnamespace = dict(vars(core))\nexec(compile(ast.fix_missing_locations(tree), '<F3-era-guard-kill>', 'exec'), namespace)\nname = 'tests.test_d165_dominance_closeout.D165DominanceCloseoutTests.test_sidecar_rejects_mixed_result_eras_at_every_cell'\nsuite = unittest.defaultTestLoader.loadTestsFromName(name)\nwith mock.patch.object(core, '_validate_common_mode_result', namespace['_validate_common_mode_result']):\n    result = unittest.TextTestRunner().run(suite)\nraise SystemExit(not result.wasSuccessful())\nPY",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 1 test in 1.617s",
          "FAILED (failures=8)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=8\\)"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d165_dominance_closeout",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          ".......................................................",
          "----------------------------------------------------------------------",
          "Ran 55 tests in 11.153s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 55 tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d165_rationale_census",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "....",
          "----------------------------------------------------------------------",
          "Ran 4 tests in 3.248s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 4 tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V7",
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

A: The baseline failure was a missing ledger, not an unjustified active occurrence. The census referenced `tests/fixtures/d165_rationale_legacy_allowlist.json`, but that file did not exist. The census now references the authorized `tests/fixtures/d165_rationale_allowlist.json`; no unlisted allowlist was created or modified. Its four exact entries justify the retained historical paragraph at `docs/paper/round7/structural-edits.md:84` and three phrases in the immutable legacy reason constant at `joulewise/dominance_closeout.py:59`. The former is bounded by its explicit SUPERSEDED banner; the latter by its LEGACY v1 block. There are no active retired-rationale occurrences. No blanket exemption or census-root reduction was added.

B: New production sidecars carry top-level `rule_id: d165_shared_sign_local_corner_replay.v2`. The validator binds every comparative result to that producer declaration and reports `d165_replay_rule_era_mismatch` at the offending result. It also binds the absolute rationale to the declared era. Explicit v1 declarations remain valid with v1 results and rationale. The original three-field producer shape declares the historical v1 era; its bytes remain readable without modification. Missing declaration never grants v2 compatibility, and invalid declarations fail closed. This compatibility rule is documented in the contract; the structural schema identifier remains unchanged so existing manifest consumers continue using the shared schema constant.

Regression coverage includes both mixed-era directions at all four cell positions, an all-results downgrade under a v2 declaration, absent/invalid declarations, rejection of a legacy absolute reason under v2, preservation of historical bytes during validation, and the actual producer's literal v2 declaration. The worked-example digest was updated in the contract and its test because the explicit declaration changes the example's serialized bytes. No floor inputs, replay arithmetic, ratios, threshold, census, branch policy, or frozen evidence were changed.

## Verification notes

V1 reproduces the missing-ledger baseline failure; V3 is the intermediate worked-example digest failure, corrected before final verification. V4 is the required expected RED mutation: a process-local AST edit disables only `rule_id != sidecar_rule_id` in the result validator. All eight mixed-era subcases then observe erroneous acceptance (`[]`) and fail. The mutation never writes production source and is removed when the process exits. V5 and V6 contain the final complete GREEN module tails after the cure.

Only the two authorized modules and one regression within the dominance-closeout module were run, sequentially, with bytecode writes disabled. No discovery suite, Claude/Codex launcher, sub-agent, hardware measurement, commit, or out-of-scope write occurred. The initial tree was clean and HEAD/upstream remained at the requested base. No blockers remain for this fix seat. Next exact step: lead reviews this scoped diff and performs the round-5 delta re-audit.

