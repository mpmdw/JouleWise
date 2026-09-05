```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "The byte-exactness witness now fixes and asserts its process-census case, removing ambient case-selection nondeterminism while preserving the live census diagnostic.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-fan-CALEXITS-EVIDENCE-BYTES-01"
  },
  "pathspec": [
    "tests/test_calibration_exits.py",
    "docs/process_traces/2026-09-04-fanout/CALEXITS-EVIDENCE-BYTES-01/01-sol-report.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_calibration_exits.PublicGovernedExitWitnessTests.test_logical_producer_delay_preserves_exact_evidence_bytes",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          ".",
          "----------------------------------------------------------------------",
          "Ran 1 test in 75.161s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_calibration_exits.PublicGovernedExitWitnessTests.test_logical_producer_delay_preserves_exact_evidence_bytes",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          ".",
          "----------------------------------------------------------------------",
          "Ran 1 test in 74.616s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V3",
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
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The focused regression passed repeatedly at this bench, but this uncommitted worktree cannot supply the acceptance row's hosted continuous-integration result.",
      "needs": "After harvest and commit, run the focused test in the hosted continuous-integration jobs and record the passing job links before closing the kernel row."
    }
  ]
}
```

## Change

The root cause is the process census, a snapshot of running commands taken after the sampler process exits. The production writer passes its event emitter to that census, so an unrelated concurrent command whose name contains `powermetrics` becomes a `powermetrics_post_teardown_census` row in `events.jsonl`. The baseline and delayed captures occur at different times and could therefore record different concurrent exit-case commands. The digest of `events.jsonl` is then stored in `instrument_evidence.json`, explaining both byte differences with one upstream cause.

The test now places a deterministic `ps` fixture first on `PATH` for both independent captures. That fixture always returns the same named case, `logical-producer-delay-immunity`, and the test asserts the exact census finding before comparing the four governed artifacts. “Governed artifact” here means a file whose bytes and digest form part of the retained validation record. Removing the fixture override makes the new assertion observe either no census row or ambient command rows instead of the registered fixed case, so the regression fails before the byte comparison can accidentally pass on a quiet machine.

| Finding | Decision | Evidence |
| --- | --- | --- |
| The two captures sampled changing ambient process membership, not different temporary-path text. | Fix the test input at the process-census boundary. | The kernel reproduction names different concurrent exit cases on each side; the writer serializes census findings through its event emitter. |
| `instrument_evidence.json` differed only because it embeds the `events.jsonl` digest. | Make no independent evidence-manifest change. | Both repeated focused runs passed all four artifact comparisons after the event input was fixed. |
| The live census is a useful diagnostic for escaped sampler processes. | Preserve production behavior and isolate only this suspension-immunity fixture. | The test still requires exactly one census event with an exact finding. |
| No hardware, operator action, schema choice, or unresolved policy choice is involved. | No `NEEDS_RULING` item is required. | The kernel has no dependency or hardware fence and explicitly permits a fixture-side cure. |

The forcing problem was to distinguish producer-delay effects from unrelated machine load without weakening exact comparison. Suppressing the production census would discard diagnostic evidence; sorting live findings would stabilize order but not changing membership; accepting variable rows would weaken byte exactness. The selected fixture-side option holds census input constant while leaving the producer delay as the only changed factor. As a worked example, the old baseline could record `case-A` while the later capture recorded `case-B`; both now record the fixed `logical-producer-delay-immunity` case, so a difference can only arise downstream of the injected producer delay or another genuine fixture defect.

## Verification notes

The repository-wide suite was not run, as required by the preflight rule. The focused test was executed twice against the final change and passed both times. Hosted continuous integration remains the only outstanding acceptance evidence; it requires the magistrate's post-harvest commit and runner.

## Residual risk

The production census intentionally remains dependent on live machine state because its purpose is to disclose unexpected sampler processes. This change establishes deterministic test evidence; it does not claim that two separate live captures taken under different process populations should be byte-identical.
