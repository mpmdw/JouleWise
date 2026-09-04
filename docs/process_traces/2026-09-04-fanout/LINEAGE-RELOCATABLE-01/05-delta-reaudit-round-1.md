```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "LR-01 is cured and the focused cold-gate tests pass, but the exported direct relocation API ignores the carrier's source-locator binding, so fix round 1 is not landable.",
  "workspace": {
    "base_requested": "68ae0b7ba82c83b2ab3d1b2e8e3687bcab99fe2a",
    "base_mode": "exact",
    "head_start": "68ae0b7ba82c83b2ab3d1b2e8e3687bcab99fe2a",
    "head_end": "68ae0b7ba82c83b2ab3d1b2e8e3687bcab99fe2a",
    "upstream_end": "68ae0b7ba82c83b2ab3d1b2e8e3687bcab99fe2a",
    "branch": "feat/2026-09-04-fan-LINEAGE-RELOCATABLE-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/LINEAGE-RELOCATABLE-01/05-delta-reaudit-round-1.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {
        "id": "DR-01",
        "severity": "should_fix",
        "location": "joulewise/arm_readiness.py:10279",
        "text": "The exported authenticate_launch_lineage relocation_carrier path validates source_locator_sha256 only as 64 lowercase hex and never compares it to a locator. A carrier with a deliberately wrong locator digest still authenticates the relocated lineage, bypassing the fix report's claimed source-locator binding.",
        "counterfactual": "Reject public carrier use without an authenticated locator, or require a pre-authenticated relocation context whose source_locator_sha256 was matched before direct lineage replay; add a direct-API regression with a wrong locator digest."
      }
    ],
    "refuter_dispositions": [
      {
        "id": "LR-01",
        "status": "CURED",
        "evidence": "The magistrate section now expressly adopts NR-1 through NR-3 and names all six refusal legs; the focused positive/refusal tests pass."
      }
    ],
    "same_signature": "DR-01 is distinct from LR-01: LR-01 was missing authority; DR-01 is a new direct-API binding bypass in the authorized implementation."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_arm_readiness tests.test_launch_window",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 82 tests in 159.826s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 82 tests in [0-9.]+s[\\s\\S]*OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nimport io, unittest\nfrom unittest import mock\nfrom joulewise import arm_readiness as readiness\nfrom tests.test_arm_readiness import LaunchLineageRelocationTests\ncase=LaunchLineageRelocationTests('test_moved_source_authenticates_only_with_explicit_carrier')\nwith mock.patch.object(readiness,'_load_launch_lineage_relocation',side_effect=readiness.LaunchLineageError('launch_binding_mismatch','counterfactual carrier dispatch disabled')):\n result=unittest.TextTestRunner(stream=io.StringIO()).run(case)\nassert result.testsRun==1 and len(result.errors)==1 and not result.failures\nassert 'counterfactual carrier dispatch disabled' in result.errors[0][1]\nprint('COUNTERFACTUAL_BITES testsRun=1 errors=1 failures=0')\nprint('carrier dispatch disabled => named moved-source regression rejects')\nPY",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["COUNTERFACTUAL_BITES testsRun=1 errors=1 failures=0", "carrier dispatch disabled => named moved-source regression rejects"]},
      "expected": {"exit_code": 0, "tail_regex": "^COUNTERFACTUAL_BITES testsRun=1 errors=1 failures=0[\\s\\S]*named moved-source regression rejects$"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nfrom joulewise import arm_readiness as readiness\nfrom tests.test_arm_readiness import LaunchLineageRelocationTests\ncase=LaunchLineageRelocationTests('test_relocation_source_locator_digest_is_mandatory'); case.setUp()\ntry:\n case.carrier['source_locator_sha256']='0'*64; case._rewrite_carrier()\n result=readiness.authenticate_launch_lineage(case.lineage,require_completion=False,relocation_carrier=case.carrier_path)\n print('DIRECT_BYPASS_ACCEPTED'); print(result['pack_id']); print(result['consumption_sha256']==case.lineage['consumption']['sha256'])\nfinally: case.doCleanups()\nPY",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["DIRECT_BYPASS_ACCEPTED", "d117_floor_qwen3-1p7b_v5", "True"]},
      "expected": {"exit_code": 0, "tail_regex": "^DIRECT_BYPASS_ACCEPTED[\\s\\S]*True$"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "base=$(git merge-base origin/main HEAD); for p in RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json docs/decision_log.md docs/process_traces/2026-09-04-fanout/01-magistrate-rulings.md; do if git diff --quiet \"$base\"..HEAD -- \"$p\"; then printf 'NO_DELTA %s\\n' \"$p\"; else printf 'DELTA %s\\n' \"$p\"; fi; done",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["NO_DELTA RUN_STATE.md", "NO_DELTA TASK_QUEUE.md", "NO_DELTA docs/process/state_kernel.json", "NO_DELTA docs/decision_log.md", "NO_DELTA docs/process_traces/2026-09-04-fanout/01-magistrate-rulings.md"]},
      "expected": {"exit_code": 0, "tail_regex": "^NO_DELTA RUN_STATE.md[\\s\\S]*NO_DELTA docs/process_traces/2026-09-04-fanout/01-magistrate-rulings.md$"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "python3 - <<'PY'\nfrom pathlib import Path\ns=Path('docs/process_traces/2026-09-04-fanout/01-magistrate-rulings.md').read_text(); s=s[s.index('## LINEAGE-RELOCATABLE-01'):]\nfor token in ('NON-authoritative relocation carrier','post-hoc analysis','live launch and campaign replay remain absolute-path','preserve every existing artifact-specific refusal code','same-byte/same-pack relocation','tamper','committed-pack-change','repository-relative-move','swapped-chain','traversal','symbolic-link'): assert token in s\nprint('LR-01 CURED: NR-1..NR-3 and six refusal legs ruled')\nPY",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["LR-01 CURED: NR-1..NR-3 and six refusal legs ruled"]},
      "expected": {"exit_code": 0, "tail_regex": "^LR-01 CURED: NR-1\\.\\.NR-3 and six refusal legs ruled$"}
    },
    {
      "id": "V6",
      "kind": "lint",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile joulewise/arm_readiness.py scripts/launch_window.py tests/test_arm_readiness.py tests/test_launch_window.py && git diff --check 64df15d8cee8097791b8a690faafc6a572918205..68ae0b7ba82c83b2ab3d1b2e8e3687bcab99fe2a",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Per the touched-module preflight rule, no untampered analysis-consumer module was executed; their existing calls also do not expose relocation_carrier.",
      "needs": "Lead decides whether user-facing analysis-consumer plumbing belongs in this mission after DR-01 is fixed."
    }
  ]
}
```

## Findings

### DR-01 — should_fix — direct relocation API ignores the locator binding

`authenticate_launch_lineage` is exported and accepts a raw
`relocation_carrier`, but `_load_launch_lineage_relocation` only checks that
`source_locator_sha256` is shaped like a digest. The comparison occurs only in
`authenticate_bundle_launch_lineage` at `joulewise/arm_readiness.py:11017-11022`.
The executed V3 counterexample changes the carrier digest to sixty-four zeroes
and calls the direct API; the relocated lineage is still accepted. This
contradicts the fix report's claimed source-locator binding and leaves the
public direct path able to use a carrier that was not matched to its locator.

LR-01 is **CURED**: the magistrate now explicitly rules NR-1 through NR-3, and
the named moved-source positive plus tamper, committed-pack-change,
repository-relative-move, swapped-chain, traversal, and symbolic-link legs all
passed in V1. V2 also shows the positive regression bites when carrier dispatch
is disabled.

Same-signature statement: DR-01 is not a relabeling of LR-01. LR-01 concerned
absent authority; DR-01 is a new binding gap introduced by the fix-round API.

## Residual risk

Only the two test modules touched by fix round 1 were run. The unchanged
analysis-engine, floor-extraction, whole-window, and reduce callers were not
executed, and none currently forwards a relocation carrier; the lead should
decide whether that user-facing plumbing is part of this mission after DR-01.
