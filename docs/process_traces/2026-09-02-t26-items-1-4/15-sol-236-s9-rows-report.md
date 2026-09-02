```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Drafted and validated all seven S9 kernel rows within the single authorized output file.",
  "workspace": {
    "base_requested": "10845c14",
    "base_mode": "exact",
    "head_start": "10845c14e7ef77c6f46013b18acc8d8569900d8a",
    "head_end": "10845c14e7ef77c6f46013b18acc8d8569900d8a",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [
    "docs/process_traces/2026-09-02-t26-items-1-4/15-s9-kernel-rows-draft.json"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "python3 -c 'import json; k=json.load(open(\"docs/process/state_kernel.json\")); print({lane:max(t[\"rank\"] for t in k[\"tasks\"].values() if t[\"lane\"]==lane) for lane in (\"agent\",\"ed_external\",\"quiet_mac\")})'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "{'agent': 119, 'ed_external': 70, 'quiet_mac': 14}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "'agent': 119.*'ed_external': 70.*'quiet_mac': 14"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 \"$TMPDIR/validate_s9_kernel_rows.py\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PASS gen_state.validate merged kernel with 7 draft tasks",
          "PASS exact task key set matches T26-RULING-INSTALL-01",
          "PASS lane ranks unique; draft agent=121..126 and ed_external=71"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PASS lane ranks unique; draft agent=121\\.\\.126 and ed_external=71"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 scripts/gen_state.py --check",
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
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --porcelain",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "?? docs/process_traces/2026-09-02-t26-items-1-4/15-s9-kernel-rows-draft.json"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^\\?\\? docs/process_traces/2026-09-02-t26-items-1-4/15-s9-kernel-rows-draft\\.json$"
      }
    }
  ],
  "flags": []
}
```

## Rows

| ID | Lane | Rank | Priority | Evidence sources |
|---|---:|---:|---|---|
| `S9-01B-REFUSAL-PRODUCER-CHECK-01` | agent | 121 | `p1_phase_gate` | `FINDINGS-TABLE.md:64-67`; `raw/enum-G8-sol-report.md:112-126` |
| `S9-02-W10-SCOPE-P256-M1-01` | agent | 122 | `p1_phase_gate` | `raw/enum-G5.md:228-266` |
| `S9-03-GAMMA-PREFILL-PROMPT-OWNER-01` | agent | 123 | `p2_next_slice` | `raw/enum-G2.md:38-48` |
| `S9-04-GAMMA-ROSTER-CHECK-01` | agent | 124 | `p2_next_slice` | `raw/enum-G3.md:307-316` |
| `S9-05-CAL-SCREEN-FLOOR-RULING-01` | ed_external | 71 | `p2_next_slice` | `raw/enum-G2.md:451-470` |
| `S9-06-WINDOW-T0-GO-RECEIPT-GATE-01` | agent | 125 | `p1_phase_gate` | `raw/enum-G6.md:411-417,494` |
| `S9-12-L10-REHEARSAL-SCHEDULE-01` | agent | 126 | `p1_phase_gate` | `raw/enum-G8-sol-report.md:130-134` |

## Executed evidence

Scratch validation result:

```text
PASS gen_state.validate merged kernel with 7 draft tasks
PASS exact task key set matches T26-RULING-INSTALL-01
PASS lane ranks unique; draft agent=121..126 and ed_external=71
```

The untouched kernel passed `python3 scripts/gen_state.py --check` with exit 0 and no output.

Final workspace state:

```text
?? docs/process_traces/2026-09-02-t26-items-1-4/15-s9-kernel-rows-draft.json
```

## Change

Created the seven-row JSON draft with mandated authorities, D-170 hard/start/pending dependencies, acceptance checks, evidence pins, and quiet-window fences.

## Verification notes

The existing rank maxima are agent `119`, ed_external `70`, and quiet_mac `14`.

The priority vocabulary is `p0_safety`, `p1_phase_gate`, `p2_next_slice`, `p3_hardening_candidates`, `p3_research_expansion`, `p3_tooling`, and `p4_polish`.

Task status `pending` is not valid. The vocabulary is `queued`, `active`, `partial`, `blocked`, and `shelved`; validator invariant 3 requires `blocked` for every row carrying a hard/start/pending dependency.