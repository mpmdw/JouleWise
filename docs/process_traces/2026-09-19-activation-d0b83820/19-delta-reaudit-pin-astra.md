```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "F1 and N1 are repaired with successful negative oracles; no introduced defect found; five inherited nits remain queue data; quick-tier failure is environmental.",
  "workspace": {
    "base_requested": "ff788ef7",
    "base_mode": "exact",
    "head_start": "d3c8b3559a3c635e43de46e98918e0e468201919",
    "head_end": "d3c8b3559a3c635e43de46e98918e0e468201919",
    "upstream_end": "d3c8b3559a3c635e43de46e98918e0e468201919",
    "branch": "HEAD (detached; matches fix/2026-09-19-head-pin-test-drift)"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 0, "nit": 5},
    "findings": [
      {
        "id": "N2",
        "severity": "nit",
        "summary": "Head-fixture selection remains label-based.",
        "call_site": "tests/test_campaign_generator_core.py:123",
        "counterfactual": "Inspection: adding a differently labelled generator with the same declared head pin would omit its historical fixture and produce a drift failure.",
        "disposition": "Inherited; queue data, no further pre-merge round."
      },
      {
        "id": "N3",
        "severity": "nit",
        "summary": "The r6 cutoff assertion is not explicitly bound to the default anchor.",
        "call_site": "tests/test_calibration_bracketing.py:643",
        "counterfactual": "Inspection: advancing DEFAULT_ACCEPTANCE_BOUND_PATH to r7 leaves the sequence-76 assertion reading r6, rather than testing the new default's cutoff.",
        "disposition": "Inherited; queue with the next default-anchor change."
      },
      {
        "id": "N4",
        "severity": "nit",
        "summary": "Two generation fixtures place the clone beneath the output root.",
        "call_site": "tests/test_d117_floor_qwen3_v5_generate.py:802 and :850",
        "counterfactual": "Inspection: a future recursive output-root inventory would include repository/** as generated output.",
        "disposition": "Inherited; queue data, no current recursive inventory failure."
      },
      {
        "id": "N5",
        "severity": "nit",
        "summary": "The historical fixture digest is self-checked in three places.",
        "call_site": "tests/test_campaign_generator_core.py:127; tests/test_arm_readiness_evidence_packauth.py:548; tests/test_d117_floor_qwen3_v5_generate.py:284",
        "counterfactual": "Inspection: inconsistent fixture bytes and digest produce redundant failures at all three consumers; consolidating the invariant would preserve detection.",
        "disposition": "Inherited; optional cleanup queue data."
      },
      {
        "id": "N6",
        "severity": "nit",
        "summary": "_commit_fixture_pin hardcodes head.json.",
        "call_site": "tests/test_calibration_ledger.py:650",
        "counterfactual": "Inspection: changing self.pin's filename at setUp leaves git add targeting head.json and fails fixture setup.",
        "disposition": "Inherited; optional cleanup queue data."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --stat ff788ef7 HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": [" 2 files changed, 15 insertions(+), 1 deletion(-)"]},
      "expected": {"exit_code": 0, "tail_regex": "2 files changed, 15 insertions\\(\\+\\), 1 deletion\\(-\\)"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/head-pin-delta-d3c8b355/oracles.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Restored probe: "]},
      "expected": {"exit_code": 0, "tail_regex": "Restored probe:"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_campaign_generator_core",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 7 tests in 2.492s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_d117_floor_qwen3_v5_generate",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 13 tests in 13.439s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_arm_readiness_evidence_packauth",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 27 tests in 83.515s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_calibration_bracketing",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 92 tests in 0.563s", "OK (skipped=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=1\\)"}
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_calibration_ledger",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 95 tests in 10.370s", "OK (skipped=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=1\\)"}
    },
    {
      "id": "V8",
      "kind": "suite",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B scripts/quick_suite.py --tier quick --workers 4",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["QUICK SUMMARY tier=quick modules=153 excluded=85 failures=1 seconds=202.581 result=FAIL"]},
      "expected": {"exit_code": 0, "tail_regex": "QUICK SUMMARY.*failures=0.*result=PASS"}
    },
    {
      "id": "V9",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/head-pin-delta-d3c8b355/same_signature.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Restored probe: "]},
      "expected": {"exit_code": 0, "tail_regex": "Restored probe:"}
    },
    {
      "id": "V10",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B scripts/fixture_orphan_census.py --fail-on-orphans",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 2, "tail": ["{\"error\": \"PermissionError: [Errno 1] Operation not permitted: 'ps'\"}"]},
      "expected": {"exit_code": 0, "tail_regex": ".*"}
    }
  ],
  "flags": [
    {
      "id": "ENV1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Sandbox denies /bin/ps. Quick tier reproduces the known tests.test_axi_controller_events failure (two assertions); fixture census cannot observe processes. This delta changes neither the failing tests nor their production dependencies.",
      "needs": "Lead-controlled quick-tier replay and fixture census outside this restriction."
    }
  ]
}
```

## Findings

**E1 — Exact requested delta.** Only F1 and N1, including their import/comments: two files, +15/−1. `shutil.copy2` runs after successful cloning and historical-head installation. Its import is correctly placed. GAMMA receives `None` from `nullcontext()`, so the assertion never accesses its unbound `head_path`. No introduced defect found; `git diff --check` passes.

**E2 — F1 negative oracle passed.** In the `/tmp` clone, an **uncommitted** ALPHA `PLAN_ID` suffix `-MUTATED` now fails both determinism and contrast-linkage assertions:

```text
AssertionError: 'plan-d117-floor-qwen3-1p7b-decode-prefill-p512-v5-MUTATED' != 'plan-d117-floor-qwen3-1p7b-decode-prefill-p512-v5'

Ran 13 tests in 16.627s

FAILED (failures=2)
```

Restored the generator, then reran the determinism test:

```text
Ran 1 test in 7.607s

OK
```

**E3 — N1 negative oracle passed.** Changed only the head-path hashing branch to `sha256_bytes(path.read_bytes())`. Installed historical head bytes in the scratch clone so generation succeeds far enough to exercise the new assertion. Failure at `tests/test_campaign_generator_core.py:157`:

```text
self.assertIn(
    mock.call(head_path), head_mock.call_args_list
)
```

The exact assertion-message opening was:

```text
AssertionError: call(PosixPath('/private/tmp/head-pin-delta-d3c8b355/probe/configs/calibration/calibration_ledger_head.json')) not found in [call(PosixPath('/private/tmp/head-pin-delta-d3c8b355/probe/configs/model_panels/qwen3_4bit.json')),
```

```text
Ran 1 test in 1.023s

FAILED (failures=1)
```

Both scratch mutations were restored. Replay scripts and complete logs remain in `/tmp/head-pin-delta-d3c8b355/`.

**E4 — Individual modules all pass:** 234 tests, two skips. Exact summaries appear in V3–V7. Quick tier completed:

```text
QUICK SUMMARY tier=quick modules=153 excluded=85 failures=1 seconds=202.581 result=FAIL
```

The failing module is `tests.test_axi_controller_events`, specifically:

- `test_campaign_prebundle_process_failure_retains_identity_receipt_and_row`
- `test_campaign_zero_exit_without_finalized_bundle_is_dispatch_failure`

Both return `2` instead of expected `1` after `campaign start identity unavailable`. A direct `/bin/ps` probe raised `PermissionError: [Errno 1] Operation not permitted`. This matches the parent’s documented sandbox failure and is **not introduced by this branch**.

**E5 — Inherited nits; none warrants another pre-merge round:**

- **N2 — nit, queue:** select the fixture by declared pin when extending generator cases.
- **N3 — nit, queue:** bind the default to r6 explicitly when next changing the default anchor.
- **N4 — nit, queue:** make repository/output directories siblings before adding recursive output inventories.
- **N5 — nit, queue:** consolidating duplicate fixture self-checks is optional cleanup.
- **N6 — nit, queue:** replace `"head.json"` with `self.pin.name` during fixture cleanup.

## Residual risk

**E6 — A surviving committed-byte site exists.** `tests/test_arm_readiness_evidence_packauth.py:124` (`committed_clone`), consumed by `test_external_pinned_input_drift_is_checked_in_derivation_mode` at line 545, executes the cloned historical `d117_floor_qwen25_1p5b_v1` generator.

Executed counterfactual: removed its acceptance-pin check **uncommitted** in scratch. The test remained green:

```text
Ran 1 test in 16.610s

OK
```

Overlaying that same mutated generator into the fixture clone exposed the missing check:

```text
self.assertNotEqual(regenerate.returncode, 0)
AssertionError: 0 == 0

Ran 1 test in 9.839s

FAILED (failures=1)
```

This predates the delta and concerns a frozen historical custody snapshot, unlike the repaired live-v5 generators. Treat it as explicit coverage queue data; do not infer that this test grades working-tree historical-generator edits.

The audited worktree and scratch probe finish clean; HEAD is unchanged. No repository files were written. The next step is the lead’s unrestricted quick-tier/census replay and final verification.