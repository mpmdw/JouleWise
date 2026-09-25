```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Named requeue_overrun tests assert refusals for INV-38 and INV-52; INV-23, INV-36, and INV-37 lack row-specific entry-path witnesses.",
  "workspace": {
    "base_requested": "6e2504b1",
    "base_mode": "exact",
    "head_start": "6e2504b166a6c9b5be85b4b916adfd2d4dae814a",
    "head_end": "6e2504b166a6c9b5be85b4b916adfd2d4dae814a",
    "upstream_end": null,
    "branch": "fix/2026-09-24-a291-r3-packer"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {"row": "INV-23", "action": "wait_for", "wait_for": "gate-item (1) entry-path witness", "collision_surface": "none"},
      {"row": "INV-36", "action": "wait_for", "wait_for": "gate-item (1) entry-path witness", "collision_surface": "none"},
      {"row": "INV-37", "action": "wait_for", "wait_for": "gate-item (1) entry-path witness", "collision_surface": "none"},
      {"row": "INV-38", "action": "wait_for", "wait_for": "closure of the three missing gate-item (1) witnesses", "collision_surface": "none"},
      {"row": "INV-52", "action": "wait_for", "wait_for": "closure of the three missing gate-item (1) witnesses", "collision_surface": "none"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest -v tests.test_scored_packer.ScoredPackerTests.test_typed_seal_and_reduce_refusals tests.test_scored_packer.ScoredPackerTests.test_typed_event_digest_and_window_key_refusals tests.test_scored_packer.ScoredPackerTests.test_r5a_resealed_output_still_replays",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "test_typed_seal_and_reduce_refusals (tests.test_scored_packer.ScoredPackerTests.test_typed_seal_and_reduce_refusals) ... ok",
          "test_typed_event_digest_and_window_key_refusals (tests.test_scored_packer.ScoredPackerTests.test_typed_event_digest_and_window_key_refusals) ... ok",
          "test_r5a_resealed_output_still_replays (tests.test_scored_packer.ScoredPackerTests.test_r5a_resealed_output_still_replays) ... ok",
          "Ran 3 tests in 7.406s",
          "OK"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 3 tests in .*s\\n\\nOK"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "INV-23, INV-36, and INV-37 have checker mutations but no named test asserting a refusal code for that row through requeue_overrun; these are open gate-item (1) defects.",
      "needs": "Lead to add and run row-specific public-entry witnesses before treating gate-item (1) as closed."
    }
  ]
}
```

## Scheduling matrix

| Row | Test file:line | Witness form | Asserted code | Listed code | Note |
|---|---|---|---|---|---|
| INV-23 | **NO ENTRY-PATH WITNESS** | [Checker mutation](/Users/edr/code/wt-278ebc9e-a291p3/tests/test_scored_roster_checker.py:705) changes a split single’s `predicted_s`; it does not submit that roster to `requeue_overrun`. | — | `inv_23` | Open gate-item (1) defect. |
| INV-36 | **NO ENTRY-PATH WITNESS** | [Checker mutation](/Users/edr/code/wt-278ebc9e-a291p3/tests/test_scored_roster_checker.py:584) changes an advanced placement’s attempt to 2; it does not submit that roster to `requeue_overrun`. | — | `inv_36` | Open gate-item (1) defect. |
| INV-37 | **NO ENTRY-PATH WITNESS** | [Checker mutation](/Users/edr/code/wt-278ebc9e-a291p3/tests/test_scored_roster_checker.py:550) adds a terminal refusal for a live item; it does not submit that roster to `requeue_overrun`. | — | `inv_37` | Open gate-item (1) defect. |
| INV-38 | [test_typed_event_digest_and_window_key_refusals](/Users/edr/code/wt-278ebc9e-a291p3/tests/test_scored_packer.py:249); [test_r5a_resealed_output_still_replays](/Users/edr/code/wt-278ebc9e-a291p3/tests/test_scored_packer.py:530) | The first changes an earlier event digest before requeue; the second changes a root block’s `late` flag and reseals it before requeue. | `inv_38`; respectively `inv_38` **or** `inv_39` | `inv_38` | The second assertion accepts either replay refusal code; it does not pin `inv_38`. |
| INV-52 | [test_typed_seal_and_reduce_refusals](/Users/edr/code/wt-278ebc9e-a291p3/tests/test_scored_packer.py:214) | Sets a block’s `items` to `None`, reseals the roster, then calls `requeue_overrun`. | `inv_52` | `inv_52` | Direct typed entry refusal. |

The [seeded fuzz test](/Users/edr/code/wt-278ebc9e-a291p3/tests/test_scored_packer_fuzz.py:208) checks that checker violations receive *some* refusal at an entry point, but does not assert a refusal code for each of these rows. It does not close the three row-specific gaps.

### Run tails

```text
test_typed_seal_and_reduce_refusals (tests.test_scored_packer.ScoredPackerTests.test_typed_seal_and_reduce_refusals) ... ok
test_typed_event_digest_and_window_key_refusals (tests.test_scored_packer.ScoredPackerTests.test_typed_event_digest_and_window_key_refusals) ... ok
test_r5a_resealed_output_still_replays (tests.test_scored_packer.ScoredPackerTests.test_r5a_resealed_output_still_replays) ... ok

----------------------------------------------------------------------
Ran 3 tests in 7.406s

OK
```

## Critical path

The INV-23, INV-36, and INV-37 gate-item (1) defects require entry-path witnesses before the forger round can proceed on this criterion.