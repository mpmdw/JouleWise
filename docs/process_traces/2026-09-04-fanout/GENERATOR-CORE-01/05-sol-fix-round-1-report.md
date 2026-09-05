```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Replaced the spoofable validator-name check with behavioral production-path coverage and an exact ALPHA bypass mutation that the regression rejects; all authorized checks and origin/main byte parity pass.",
  "workspace": {
    "base_requested": "bac357d1dac79dabfcb1684a018d92a76422a907",
    "base_mode": "exact",
    "head_start": "bac357d1dac79dabfcb1684a018d92a76422a907",
    "head_end": "bac357d1dac79dabfcb1684a018d92a76422a907",
    "upstream_end": "7da20e28e795ac9aac41f774e4f5f7fa0ef29f5c",
    "branch": "feat/2026-09-04-fan-GENERATOR-CORE-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/GENERATOR-CORE-01/05-sol-fix-round-1-report.md",
    "docs/specs/generator_core.md",
    "joulewise/campaign_generator_core.py",
    "tests/test_campaign_generator_core.py"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_campaign_generator_core tests.test_d117_contrast_v5_pack tests.test_microdelta_generate_configs",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 51 tests in 17.310s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 51 tests in .*s[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_campaign_generator_core_parity.py --baseline-ref origin/main",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PARITY_DIFF_EMPTY generator=ALPHA files=120",
          "PARITY_DIFF_EMPTY generator=BETA files=120",
          "PARITY_DIFF_EMPTY generator=GAMMA files=112",
          "PARITY_OK generators=3 files=352 excluded=['generate_configs.py', 'plan_tree.json', 'plan_tree.sha256'] baseline=origin/main"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PARITY_DIFF_EMPTY generator=ALPHA files=120[\\s\\S]*PARITY_DIFF_EMPTY generator=BETA files=120[\\s\\S]*PARITY_DIFF_EMPTY generator=GAMMA files=112[\\s\\S]*PARITY_OK generators=3 files=352 .* baseline=origin/main"
      }
    }
  ],
  "flags": []
}
```

## Change

| Finding | Cure | File:line |
|---|---|---|
| F1 blocker: the old counterfactual could be spoofed by retaining the imported validator but redirecting ALPHA to a differently named local implementation. | Added one inert observer inside the shared validator. The regression now drives all three production generators, requires one final-root shared-boundary call per generator, and proves every observed validation inventory equals every emitted file. A separate temporary source mutation adds the refuter's exact same-signature local validator and redirects ALPHA; the behavioral assertion fails on that mutation. Imported-name identity is retained only as secondary coverage for the extracted mechanics. | `joulewise/campaign_generator_core.py:19`, `joulewise/campaign_generator_core.py:75`, `joulewise/campaign_generator_core.py:102`; `tests/test_campaign_generator_core.py:73`, `tests/test_campaign_generator_core.py:143`, `tests/test_campaign_generator_core.py:150`; `docs/specs/generator_core.md:35`, `docs/specs/generator_core.md:78` |
| F2 blocker: the earlier seven-path landing scope excluded three process traces. | This fix round's authoritative scope explicitly includes `docs/process_traces/2026-09-04-fanout/GENERATOR-CORE-01/**`; the existing traces and this report are therefore authorized. No state or other out-of-scope path was edited. | `docs/process_traces/2026-09-04-fanout/GENERATOR-CORE-01/04-refuter-merge-base.md:171`; this report, line 76 |

The observer defaults to `None` and runs only after all relative paths pass the
existing safety checks. Materializing the iterable as a tuple preserves the
validator's previous one-pass consumption while giving the observer the exact
inventory validated by the production call.

## Verification notes

An initial focused development run expected one total validator call and
exposed GAMMA's existing two-stage topology: it validates both the final root
and a staging root. The final assertion requires exactly one final-root call
and checks every final and staging call against the complete emitted
inventory. The authorized final suite and parity command are clean.
