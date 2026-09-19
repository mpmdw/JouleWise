```json
{
 "schema": "claude-codex-report/v1",
 "genre": "implementation",
 "status": "findings",
 "completion": "complete",
 "summary": "B1 implemented in exactly five scoped files; focused and frozen tests pass; quick-tier failure reproduces at base under blocked process observation.",
 "workspace": {
  "base_requested": "b3abce08",
  "base_mode": "exact",
  "head_start": "b3abce08f388cb061ebf65ed8e7249ad286fae7d",
  "head_end": "b3abce08f388cb061ebf65ed8e7249ad286fae7d",
  "upstream_end": "b3abce08f388cb061ebf65ed8e7249ad286fae7d",
  "branch": "fix/2026-09-19-generator-head-pin-semantic"
 },
 "pathspec": [
  "configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py",
  "configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py",
  "tests/test_campaign_generator_core.py",
  "tests/test_d117_floor_qwen3_v5_generate.py",
  "tests/test_generator_head_pin_relation.py"
 ],
 "unowned_dirty": [],
 "verdict": {
  "implementation": "implemented",
  "acceptance": "pending_verification"
 },
 "verification": [
  {
   "id": "V1",
   "kind": "suite",
   "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_generator_head_pin_relation tests.test_campaign_generator_core tests.test_d117_floor_qwen3_v5_generate tests.test_d117_v3_family tests.test_arm_readiness_evidence_packauth > /tmp/head-pin-focused.log 2>&1",
   "cwd": ".",
   "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 62 tests in 204.474s", "OK"]},
   "expected": {"exit_code": 0, "tail_regex": "OK"}
  },
  {
   "id": "V2",
   "kind": "suite",
   "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_d117_floor_qwen25_1p5b_plan tests.test_d117_floor_qwen25_7b_plan tests.test_d117_decode_contrast_plan tests.test_arm_readiness_registry > /tmp/head-pin-frozen.log 2>&1",
   "cwd": ".",
   "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 73 tests in 166.976s", "OK (skipped=1)"]},
   "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=1\\)"}
  },
  {
   "id": "V3",
   "kind": "test",
   "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python /tmp/head-pin-negative-oracles.py > /tmp/head-pin-negative-oracles.log 2>&1",
   "cwd": ".",
   "observed": {
    "result": "pass",
    "exit_code": 0,
    "tail": [
     "ORACLE rollback: exit=1",
     "AssertionError: ValueError not raised",
     "FAILED (failures=2)",
     "ORACLE rollback: expected regression failure confirmed for both generators",
     "ORACLE byte-pin: exit=1",
     "ValueError: pinned input drifted: configs/calibration/calibration_ledger_head.json",
     "FAILED (errors=2)",
     "ORACLE byte-pin: expected regression failure confirmed for both generators"
    ]
   },
   "expected": {"exit_code": 0, "tail_regex": "expected regression failure confirmed for both generators"}
  },
  {
   "id": "V4",
   "kind": "suite",
   "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python scripts/quick_suite.py --tier quick --workers 4 > /tmp/head-pin-quick.log 2>&1",
   "cwd": ".",
   "observed": {
    "result": "fail",
    "exit_code": 1,
    "tail": ["QUICK SUMMARY tier=quick modules=153 excluded=86 failures=1 seconds=209.864 result=FAIL"]
   },
   "expected": {"exit_code": 0, "tail_regex": "QUICK SUMMARY .*failures=0 .*result=PASS"}
  },
  {
   "id": "V5",
   "kind": "test",
   "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python /tmp/head-pin-baseline-process.py > /tmp/head-pin-baseline-process.log 2>&1",
   "cwd": ".",
   "observed": {
    "result": "fail",
    "exit_code": 1,
    "tail": [
     "Ran 7 tests in 3.774s",
     "FAILED (failures=2)",
     "SHARD SUMMARY index=1/1 modules=1 tests=7 failures=2 errors=0 skipped=0 result=FAIL"
    ]
   },
   "expected": {"exit_code": 0, "tail_regex": "result=PASS"}
  },
  {
   "id": "V6",
   "kind": "inspection",
   "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python scripts/fixture_orphan_census.py --fail-on-orphans > /tmp/head-pin-census.log 2>&1",
   "cwd": ".",
   "observed": {
    "result": "fail",
    "exit_code": 2,
    "tail": ["{\"error\": \"PermissionError: [Errno 1] Operation not permitted: 'ps'\"}"]
   },
   "expected": {"exit_code": 0, "tail_regex": ".*"}
  },
  {
   "id": "V7",
   "kind": "inspection",
   "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/head-pin-inspection.py",
   "cwd": ".",
   "observed": {
    "result": "pass",
    "exit_code": 0,
    "tail": [
     "PASS scope: exactly five authorized paths; no unowned dirty files",
     "PASS live generators: identical semantic helpers; byte-pin constant absent",
     "PASS custody: 19 frozen/contrast generators and plan trees byte-identical to HEAD",
     "PASS git diff --check"
    ]
   },
   "expected": {"exit_code": 0, "tail_regex": "PASS git diff --check"}
  },
  {
   "id": "V8",
   "kind": "inspection",
   "cmd": "git grep -n issued_ledger_head -- joulewise scripts",
   "cwd": ".",
   "observed": {"result": "pass", "exit_code": 1, "tail": []},
   "expected": {"exit_code": 1, "tail_regex": "^$"}
  },
  {
   "id": "V9",
   "kind": "inspection",
   "cmd": "rg -n -g '!configs/**' -g '!docs/**' -g '!*.md' 'issued_ledger_head' .",
   "cwd": ".",
   "observed": {
    "result": "pass",
    "exit_code": 0,
    "tail": ["./tests/test_generator_head_pin_relation.py:178:                    tree[\"acceptance_policy\"][\"issued_ledger_head\"],"]
   },
   "expected": {"exit_code": 0, "tail_regex": "tests/test_generator_head_pin_relation.py:178:"}
  },
  {
   "id": "V10",
   "kind": "inspection",
   "cmd": "git diff > /tmp/head-pin-change.patch\ngit diff --no-index /dev/null tests/test_generator_head_pin_relation.py >> /tmp/head-pin-change.patch\ngit apply --stat /tmp/head-pin-change.patch",
   "cwd": ".",
   "observed": {"result": "pass", "exit_code": 0, "tail": ["5 files changed, 292 insertions(+), 56 deletions(-)"]},
   "expected": {"exit_code": 0, "tail_regex": "5 files changed, 292 insertions\\(\\+\\), 56 deletions\\(-\\)"}
  }
 ],
 "flags": [
  {
   "id": "F1",
   "kind": "environment",
   "level": "nonblocking",
   "text": "Quick tier: one failing module, tests.test_axi_controller_events (two assertions); identical failures reproduced in a clean clone of b3abce08. /bin/ps is denied. Fixture orphan census also exits 2 because ps is denied; no clean census is claimed.",
   "needs": "Lead replay quick tier and fixture census in the approved environment with process observation available."
  },
  {
   "id": "F2",
   "kind": "verification_gap",
   "level": "nonblocking",
   "text": "Full unittest discovery was not run: the repository quick runner excludes five A211 modules with canonical-checkout dependencies, and this brief forbids touching that checkout. Requested focused, frozen-path, and quick commands were executed.",
   "needs": "Lead owns final review and the remaining full replay gate."
  }
 ]
}
```

## Change

Both live generators now validate the head pin’s shape, acceptance binding, schema, ordering, and equal-sequence digest after the unchanged input-drift checks. Emitted manifests contain only `{path, head_sha256}`. The comment explicitly assigns higher-sequence fork detection to runtime evaluation.

Verified ALPHA/BETA are live generators; removed their fixtures while retaining the shared frozen-path helper and constants. No commits made.

## Verification notes

The frozen-suite skip is pre-existing: an uninstalled v2 family versus the v5 registry.

Production consumer grep output was empty. The broader source search finds only the new regression assertion. Generic `file_sha256` occurrences concern unrelated artifacts.

The new test remains untracked, so ordinary `git diff --stat` lists four tracked edits; the combined patch includes all five authorized paths.

Next: lead review and replay the environmental failures with process observation available.