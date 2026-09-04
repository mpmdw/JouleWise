# FLOOR-V5-DRIFT-REPIN-01 kernel registration

## What was added

- Registered one agent-lane P1 row for CR-3 from the `_v5` floor-generator
  counter-review on branch `feat/2026-09-02-v5-floor-generator`.
- Set the row to `blocked` with one pending hard-start dependency on
  `V5-DESK-DAY-01`: the packs must be frozen before their source-byte and
  domain-hash pins can be restored. This applies the magistrate's option-1
  ruling and kernel invariant 3.
- Preserved the off-main CR-3 passage in `02-evidence-index.md` so the kernel's
  authority pointer resolves from this branch.
- Added the ID to `EXPECTED_IDS`, advanced the count tripwire from 142 to 143,
  and regenerated `TASK_QUEUE.md`.

## Verbatim kernel row

```json
{
  "acceptance": {
    "evidence": [
      "Both _v5 floor generators pin the frozen source bytes and domain hashes for the decode, prefill, and p512 condition families",
      "A counterfactual test independently drifts each of the six pins and proves the corresponding generator refuses",
      "The restored refusals preserve the frozen desk-day pack bytes and do not alter the _v5 condition-family schemas"
    ],
    "pointer": {
      "json_pointer": "/tasks/FLOOR-V5-DRIFT-REPIN-01/acceptance",
      "label": "FLOOR-V5-DRIFT-REPIN-01 acceptance",
      "path": "docs/process/state_kernel.json"
    },
    "summary": "The two _v5 floor generators restore all six source-byte and domain-hash drift refusals after their condition-family bytes are frozen."
  },
  "authority": {
    "label": "V5 floor-generator Opus counter-review CR-3, preserved from feat/2026-09-02-v5-floor-generator",
    "path": "docs/process_traces/2026-09-03-kernel-batch/02-evidence-index.md"
  },
  "dependencies": [
    {
      "evidence": null,
      "kind": "task",
      "required": "the three _v5 packs are frozen before their source-byte and domain-hash pins can be restored",
      "scope": "start",
      "state": "pending",
      "strength": "hard",
      "target": "V5-DESK-DAY-01"
    }
  ],
  "fallback": null,
  "fences": [],
  "flags": [],
  "goal": "Restore the six condition-family drift refusals (source-byte + domain-hash pins for decode/prefill families) in the `_v5` floor generators after the desk-day freeze; `_v3` carried them (d117_floor_qwen25_1p5b_v3/generate_configs.py ~:741-770), `_v5` assigns the domain hashes at runtime until the freeze",
  "id": "FLOOR-V5-DRIFT-REPIN-01",
  "lane": "agent",
  "priority": "p1_phase_gate",
  "rank": 69,
  "status": "blocked",
  "status_note": "Registered 2026-09-03 from CR-3 on branch feat/2026-09-02-v5-floor-generator. The magistrate selected option 1: kernel invariant 3 requires BLOCKED because the pack freeze owned by V5-DESK-DAY-01 is a pending hard start dependency.",
  "stop_card": null
}
```

## Test tails

```text
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_gen_state tests.test_docs_freshness
.................................................................
----------------------------------------------------------------------
Ran 65 tests in 3.721s

OK
```

```text
$ python3 scripts/gen_state.py --check
[no output; exit 0]
```
