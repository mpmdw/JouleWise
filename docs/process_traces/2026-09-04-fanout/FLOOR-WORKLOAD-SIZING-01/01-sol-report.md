```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented decision-neutral workload-margin arithmetic and documented the settled stage sizing, while live pilot evidence and the obsolete-row disposition remain gated.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-fan-FLOOR-WORKLOAD-SIZING-01"
  },
  "pathspec": [
    "docs/phase_2/floor_workload_sizing.md",
    "docs/process_traces/2026-09-04-fanout/FLOOR-WORKLOAD-SIZING-01/01-sol-report.md",
    "joulewise/workload_sizing.py",
    "tests/test_workload_sizing.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_workload_sizing",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 6 tests in 0.001s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 6 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_select_g2a_prefill_length tests.test_summarize_g2a_prefill_probe tests.test_d117_contrast_v5_pack",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 50 tests in 6.181s",
          "OK",
          "PASS built G2-a prompt ladder, configs, and manifests",
          "PASS bound G2-a inputs to the calibration window"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 50 tests in [0-9.]+s\\n\\nOK[\\s\\S]*PASS bound G2-a inputs to the calibration window"
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
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "D-166 now owns production workload selection and conflicts with treating the older effect-to-floor idea as another selector.",
      "needs": "Rule whether FLOOR-WORKLOAD-SIZING-01 is retired as superseded (recommended) or retained as a separate diagnostic study that cannot alter the v5 workload."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "No issued G2-a live record exists, so the exact prefill size, measured pilot ratios, and regenerated successor floor configurations cannot be produced at the desk.",
      "needs": "Complete the lead-owned quiet-machine G2-a window, issue its immutable summary and selection record, then generate and verify the three successor Qwen3 packs."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The arithmetic helper validates numeric domains but intentionally does not authenticate source artifacts or confer claim eligibility.",
      "needs": "Any future artifact producer must bind the pilot effect, operative floor, and claim-side bound to issued evidence before calling the helper."
    }
  ]
}
```

## Change

Added a small arithmetic module that reports two quantities required by the
settled metrology: measured effect divided by the operative floor, and measured
effect divided by the operative floor plus the claim-side bound. The result is
descriptive only; it has no threshold, pass field, or workload-selection field.
Its focused tests are counterfactual: removing the module or either ratio makes
the test module fail, and the record-shape test prevents an unruled verdict from
being added silently.

Added a scoped design that defines the forcing problem, options,
recommendation, symbolic worked example, current stage-to-size decision, and
remaining live-evidence checklist. Frozen Qwen2.5 packs were left unchanged.
The successor Qwen3 packs remain gated on the issued G2-a selection record.

| Finding or decision | Evidence | Disposition |
|---|---|---|
| The kernel row has no declared dependency, but its measured pilot evidence does not exist. | `FLOOR-WORKLOAD-SIZING-01` acceptance and the queued `V5-G2A-PREFILL-PROBE-01` row in the state kernel. | Desk arithmetic landed; live acceptance remains open. |
| D-166 fixes decode at 512 generated tokens. | D-166 index text and `04-MAGISTRATE-RULING.md` R-1. | Every successor decode stage must keep that size. |
| D-166 and its amendment make prefill size an evidence-derived resolvability decision. | G2-a ladder and selector contracts; focused V2 tests. | Use one selected rung across successor prefill stages; do not guess it now. |
| The older ratio-based selection premise conflicts with the newer production selector. | D-078 workload-sizing note compared with D-166 R-2. | NEEDS_RULING: retire the row as superseded (recommended) or authorize a separate non-selecting diagnostic study. |
| Existing Qwen2.5 packs are receipt-frozen. | `_v3` pack README, generator, and freeze attachment. | No config bytes changed. |

## Verification notes

Executed evidence:

| Command | Result | Exact tail |
|---|---|---|
| `python3 -m unittest tests.test_workload_sizing` | pass | `Ran 6 tests in 0.001s`; `OK` |
| `python3 -m unittest tests.test_select_g2a_prefill_length tests.test_summarize_g2a_prefill_probe tests.test_d117_contrast_v5_pack` | pass | `Ran 50 tests in 6.181s`; `OK`; `PASS built G2-a prompt ladder, configs, and manifests`; `PASS bound G2-a inputs to the calibration window` |
| `git diff --check` | pass | no output |

The repository-wide suite was not run, as required by the preflight rule. No
hardware, quiet-machine collection, agent launch, commit, or forbidden-file
edit was performed.

## Residual risk

Acceptance is incomplete until the live pilot exists. If the row remains a
separate study, the lead must rule its exact effect estimand, candidate set,
evidence bindings, and scheduling before any collection or configuration edit.
