```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Disappearing launch files now produce controlled errors, and a synchronized test proves that only one caller can consume launch authority.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-lineage-seams"
  },
  "pathspec": [
    "joulewise/arm_readiness.py",
    "tests/test_analysis_inputs.py",
    "tests/test_arm_readiness_lifecycle.py",
    "docs/process_traces/2026-09-04-fanout/lineage-seams/01-sol-report.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_analysis_inputs",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 6 tests in 0.018s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 6 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_arm_readiness_lifecycle",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 67 tests in 123.900s", "OK (skipped=3)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 67 tests.*OK \\(skipped=3\\)"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_analysis_inputs.RealizedIdentityDispatchTests.test_bundle_reader_maps_second_resolve_vanish_to_named_lineage_refusal tests.test_arm_readiness_lifecycle.ArmReadinessLifecycleTests.test_consumed_manifest_second_resolve_vanish_is_lineage_refusal tests.test_arm_readiness_lifecycle.ArmReadinessLifecycleTests.test_atomic_launch_capability_race_exactly_one_consumer_and_replay_refuses",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 3 tests in 0.044s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 3 tests.*OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_analysis_inputs.RealizedIdentityDispatchTests.test_bundle_reader_maps_second_resolve_vanish_to_named_lineage_refusal",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FileNotFoundError: <temporary>/launch-manifest.json", "FAILED (errors=1)"]
      },
      "expected": {"exit_code": 1, "tail_regex": "FileNotFoundError:.*FAILED \\(errors=1\\)"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_arm_readiness_lifecycle.ArmReadinessLifecycleTests.test_consumed_manifest_second_resolve_vanish_is_lineage_refusal",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FileNotFoundError: <temporary>/launch-manifest.json", "FAILED (errors=1)"]
      },
      "expected": {"exit_code": 1, "tail_regex": "FileNotFoundError:.*FAILED \\(errors=1\\)"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_arm_readiness_lifecycle.ArmReadinessLifecycleTests.test_atomic_launch_capability_race_exactly_one_consumer_and_replay_refuses",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["AssertionError: 0 != 1 : ['readiness_output_collision', 'launch_consumption_invalid']", "FAILED (failures=1)"]
      },
      "expected": {"exit_code": 1, "tail_regex": "readiness_output_collision.*FAILED \\(failures=1\\)"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The lifecycle module retains three pre-existing skipped tests outside this change; the synchronized consumption race now runs.",
      "needs": ""
    }
  ]
}
```

## Change

Strict path resolution means asking the operating system to confirm that a named file exists and to return its canonical path, the unique normalized location for that file. A lineage refusal is a controlled error carrying a stable reason code, which is a machine-readable label explaining why recorded launch history could not be authenticated. Both later strict resolutions now convert a disappearing file or a path-resolution loop, a cycle of links that prevents a unique location, into `launch_binding_mismatch`; the analysis reader, the component that admits recorded bundles for analysis, therefore receives the controlled refusal instead of an operating-system exception.

An atomic no-clobber write means creating a file only when no file already occupies its name. A barrier is a synchronization point that holds each test caller until every caller has arrived. The restored race test sends both callers through the public launcher, the user-callable launch entry point, holds them at the real atomic no-clobber write, and proves that only the writer that creates the consumption record proceeds. Replay means a later attempt to use that already-consumed record; the test proves replay returns `readiness_record_consumed`, the stable reason code for an already-used launch capability.

A test fixture is the prepared set of files and objects from which a test starts. An arm record is stored proof that launch prerequisites passed. The earlier test fixture rebuilt that record from obsolete generic evidence, while the current fixture begins with a launch context, the complete set of authenticated inputs presented for consumption. This removes the obsolete setup dependency without substituting a fake write or weakening the winner, loser, or replay assertions.

A counterfactual mutation means temporarily removing the behavior under test to confirm that the test fails. A sidecar is a file adjacent to a primary record that stores a computed content check.

An alias is an alternate pathname for the same location. A recorded artifact is a file produced during a test. A test harness is the code that drives a test.

An exception boundary is a `try` and `except` block that converts an operating-system failure into a controlled error. The single-use linearization point is the exact write that chooses the sole successful caller.

| Topic | Finding | Decision |
|---|---|---|
| Disappearing path | A later strict resolution could escape as an operating-system exception. | Translate either later resolution failure into the controlled lineage refusal. |
| Blocked setup | Arm-record reconstruction depended on obsolete evidence shapes unrelated to consumption. | Begin from the current complete launch context and retain the production launcher and writer. |
| Concurrent consumption | Unsynchronized callers might miss the actual contested write during a test run. | Hold both callers at the production write, then assert the winner, loser, and replay outcomes. |

### Mechanical first-use table

The mechanical first-use check searched this report for each technical phrase and returned its earliest line; each earliest line contains the stated plain meaning.

| Technical phrase | First line | Plain meaning present there | Result |
|---|---:|---|---|
| strict path resolution | 115 | operating-system existence check and normalized location | pass |
| canonical path | 115 | unique normalized location | pass |
| lineage refusal | 115 | controlled error with a machine-readable reason | pass |
| reason code | 115 | machine-readable label for the refusal | pass |
| path-resolution loop | 115 | cycle of links preventing a unique location | pass |
| analysis reader | 115 | component that admits recorded bundles | pass |
| atomic no-clobber write | 117 | create only if the name is unused | pass |
| barrier | 117 | synchronization point waiting for every caller | pass |
| public launcher | 117 | user-callable launch entry point | pass |
| replay | 117 | later attempt to reuse a consumed record | pass |
| test fixture | 119 | prepared files and objects forming test input | pass |
| arm record | 119 | stored proof that launch prerequisites passed | pass |
| launch context | 119 | complete authenticated inputs presented for consumption | pass |
| counterfactual mutation | 121 | temporary removal of the behavior under test | pass |
| sidecar | 121 | adjacent file holding a computed content check | pass |
| alias | 123 | alternate pathname for the same location | pass |
| recorded artifact | 123 | file produced during a test | pass |
| test harness | 123 | code that drives a test | pass |
| exception boundary | 125 | conversion block for operating-system failures | pass |
| single-use linearization point | 125 | exact write choosing the sole successful caller | pass |

Mechanical command:

```text
for phrase in 'strict path resolution' 'canonical path' 'lineage refusal' 'reason code' 'path-resolution loop' 'analysis reader' 'atomic no-clobber write' 'barrier' 'public launcher' 'replay' 'test fixture' 'arm record' 'launch context' 'counterfactual mutation' 'sidecar' 'alias' 'recorded artifact' 'test harness' 'exception boundary' 'single-use linearization point'; do awk 'BEGIN { prose=0 } /^## Change$/ { prose=1 } prose { print NR ":" $0 }' docs/process_traces/2026-09-04-fanout/lineage-seams/01-sol-report.md | rg -i -m1 -F "$phrase"; done
```

## Verification notes

The first lifecycle-module execution failed because the test target used macOS's `/var` alias while the recorded artifact used the canonical `/private/var` spelling. Resolving the target before the disappearance substitution corrected the test harness; the production change was unaffected.

Final module evidence:

```text
$ python3 -m unittest tests.test_analysis_inputs
......
----------------------------------------------------------------------
Ran 6 tests in 0.018s

OK

$ python3 -m unittest tests.test_arm_readiness_lifecycle
----------------------------------------------------------------------
Ran 67 tests in 123.900s

OK (skipped=3)
```

The counterfactual mutations removed each exception boundary in turn. Removing the first boundary produced raw `FileNotFoundError` and `FAILED (errors=1)` in the analysis-reader test; removing the second boundary produced the same raw exception and result in the lineage test. Replacing the atomic no-clobber primary write with an ordinary write produced `['readiness_output_collision', 'launch_consumption_invalid']` and `FAILED (failures=1)`, showing that the synchronized race detects loss of the single-use linearization point. The later `readiness_output_collision` came from the sidecar only after both callers had incorrectly passed the mutated primary write.

After restoring production code, the focused tests ended with:

```text
$ python3 -m unittest tests.test_analysis_inputs.RealizedIdentityDispatchTests.test_bundle_reader_maps_second_resolve_vanish_to_named_lineage_refusal tests.test_arm_readiness_lifecycle.ArmReadinessLifecycleTests.test_consumed_manifest_second_resolve_vanish_is_lineage_refusal tests.test_arm_readiness_lifecycle.ArmReadinessLifecycleTests.test_atomic_launch_capability_race_exactly_one_consumer_and_replay_refuses
...
----------------------------------------------------------------------
Ran 3 tests in 0.044s

OK
```

The repository-wide test suite was not run, as required by the preflight rule.
