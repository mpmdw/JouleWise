```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "The requested delta closes N-1/N-2, supports the SF-2 reversal, and corrects SF-1 wording; production is unchanged.",
  "workspace": {
    "base_requested": "6881709d",
    "base_mode": "exact",
    "head_start": "17843715c9b05578902e561d667b151fe0fb9abc",
    "head_end": "17843715c9b05578902e561d667b151fe0fb9abc",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 0, "nit": 0},
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff 6881709d..17843715 -- tests/fixtures/arm_clock.py tests/test_arm_readiness_lifecycle.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["             launch_inputs = launch_window._assemble_launch_inputs(args)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "launch_inputs = launch_window\\._assemble_launch_inputs"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "python3 -B -c 'import inspect; from unittest.mock import Mock; from tests.fixtures.arm_clock import coherent_clock_anchor; f = Mock(side_effect=coherent_clock_anchor); assert f(object()) == coherent_clock_anchor(); print(\"positional side_effect: PASS\"); s = inspect.signature(coherent_clock_anchor); assert s.parameters[\"clock_gettime_ns\"].kind == inspect.Parameter.POSITIONAL_OR_KEYWORD; assert all(s.parameters[k].kind == inspect.Parameter.KEYWORD_ONLY for k in (\"raw_ns\", \"skew_ns\", \"drift_ns\")); print(\"signature: PASS\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["positional side_effect: PASS", "signature: PASS"]
      },
      "expected": {"exit_code": 0, "tail_regex": "signature: PASS"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --stat 6881709d..17843715 -- joulewise scripts; git diff --check 6881709d..17843715; git status --short --branch; git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["17843715c9b05578902e561d667b151fe0fb9abc"]
      },
      "expected": {"exit_code": 0, "tail_regex": "17843715c9b05578902e561d667b151fe0fb9abc"}
    }
  ],
  "flags": []
}
```

## Findings

None in the requested delta.

1. **N-1 — closed.** `coherent_clock_anchor(clock_gettime_ns=None, *, raw_ns=…, skew_ns=…, drift_ns=…)` accepts and ignores the positional argument. Both patches exist at `tests/test_arm_readiness_integration.py:317` and `tests/test_arm_readiness_lifecycle.py:585`. They now accept the production call at `joulewise/clock_reference.py:178`:
   ```python
   anchor = sample_anchor(clock_gettime_ns)
   ```
   V2 tails: `positional side_effect: PASS`, `signature: PASS`. A keyword-only replacement would raise `TypeError` before returning an anchor at that call site.

2. **N-2 — closed.** The docstring names all three production locations comparing REALTIME−RAW offsets. `rg -n 'realtime_ns' joulewise` confirms the relevant arithmetic at `arm_readiness.py:6783–6787,6830–6833`, `_derive_clock_attestation` in `arm_readiness_evidence_t0.py:1167–1168`, and `t0_rehearsal.py:643–644`. The common constant cancels between offsets; no inspected anchor predicate compares `realtime_ns` with wall-clock now.

3. **SF-2 reversal — supported.** `_derive_reason_code_coverage`, `joulewise/arm_readiness_evidence.py:2312`, supplies:
   ```python
   "tests.test_arm_readiness_integration.ArmReadinessIntegrationTests."
   "test_refusal_registry_coverage_and_defensive_unreachable_justifications"
   ```
   `_run_suite` calls `_execute_unittest_suite_subprocess(context.repository, test_ids)` at line 750. That function launches an isolated interpreter with `cwd=repository`; its child installs the repository first on `sys.path` and executes `loader.loadTestsFromNames(test_ids)` at line 573. The named module imports the helper—grep tail: `36:from tests.fixtures.arm_clock import coherent_clock_anchor`. Therefore the helper must accompany this copied-repository execution path. The copy remains at lifecycle lines 425–427 with `exist_ok=True`; its comment names both the mechanism and the reported deletion failure.

4. **SF-1 wording — closed within scope.** Lifecycle lines 906–908 cite CPU `96.1 s -> 59.1 s`, approximately `-38 %`, and per-thread wall `-1.4 s` against the 30-second join. The comment no longer says “dominated.” These numbers match review 90’s recorded measurements; this audit did not remeasure them.

5. **No other change.** Full delta: two files, 32 insertions, seven deletions. Production-stat output was empty; `git diff --check` produced no diagnostics. HEAD remained unchanged and the worktree clean. No files written.

6. **Same-signature statement.** No repeated failure signature was found among these delta items. The SF-2 deletion failure is the lead-reported counterfactual supporting restoration, not a newly observed failure here.

## Residual risk

This read-only audit does not discharge the earlier four-shard race obligation or independently rerun the copied-repository deletion counterfactual. A heredoc smoke attempt was blocked by the sandbox’s temporary-file restriction; the equivalent positional-signature smoke passed using `python3 -B -c`. Full suites and live hardware checks were not run.