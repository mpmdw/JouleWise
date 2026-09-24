```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented the A281a registration, scored packer, and scored reducer contracts; named tests and file-level mutation sweeps pass.",
  "workspace": {
    "base_requested": "c8d5d1f9ab4b52db385642d28b8d6d877cc63e50",
    "base_mode": "exact",
    "head_start": "c8d5d1f9ab4b52db385642d28b8d6d877cc63e50",
    "head_end": "c8d5d1f9ab4b52db385642d28b8d6d877cc63e50",
    "upstream_end": "c8d5d1f9ab4b52db385642d28b8d6d877cc63e50",
    "branch": "feat/2026-09-24-a281a-registration-packer-reducer"
  },
  "pathspec": [
    "joulewise/scored_registration.py",
    "joulewise/scored_packer.py",
    "joulewise/scored_reduce.py",
    "tests/test_scored_registration.py",
    "tests/test_scored_packer.py",
    "tests/test_scored_reduce.py"
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
      "cmd": "python3 -B -m unittest tests.test_scored_registration tests.test_scored_packer tests.test_scored_reduce",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 13 tests in 1.501s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 13 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B /tmp/a281a_final_remaining_mutants.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "RESULT scored_registration.py generated 90 killed 90 survived 0 seconds 35.3",
          "RESULT scored_reduce.py generated 108 killed 108 survived 0 seconds 179.8"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "RESULT scored_registration.py generated 90 killed 90 survived 0 seconds .*\\n.*RESULT scored_reduce.py generated 108 killed 108 survived 0 seconds .*"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B /tmp/a281a_final_packer_mutants.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["RESULT scored_packer.py generated 152 killed 152 survived 0 seconds 184.1"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "RESULT scored_packer.py generated 152 killed 152 survived 0 seconds .*"
      }
    },
    {
      "id": "V4",
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
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Registration binds the sizing-receipt and item-set hashes but does not inspect their external contents; the magistrate should confirm the AP-5M provenance and canonical manifest encoding.",
      "needs": "Confirm the receipt's delta source and the item-set digest encoding in the owning plan."
    }
  ]
}
```

## Change

| Clause | Implementation and defect-shaped regression |
|---|---|
| G1 | [Registration.from_mapping](/Users/edr/code/wt-d8cc9c0a-a281a/joulewise/scored_registration.py:89) requires exact fields and types, freezes values, hashes canonical JSON, asserts ruled constants, validates timing and physical ceilings, and enforces the registered drift-budget formula. [Missing-key, bool, coherence, and constant tests](/Users/edr/code/wt-d8cc9c0a-a281a/tests/test_scored_registration.py:43) refuse inputs the round-1 code could not structurally validate. |
| G2 | [pack](/Users/edr/code/wt-d8cc9c0a-a281a/joulewise/scored_packer.py:212) takes the registration, binds its digest, marks pilot rosters unready, and refuses an excessive registered gap. [Pilot and registered-gap tests](/Users/edr/code/wt-d8cc9c0a-a281a/tests/test_scored_packer.py:21) cover both modes. |
| G3 | [requeue_overrun](/Users/edr/code/wt-d8cc9c0a-a281a/joulewise/scored_packer.py:287) checks both digests, derives each single’s worst case, tracks distinct stages and the packed-roster root, recomputes executed gaps, and attributes elapsed time per affected item. [Digest, worst-case, terminal, and innocent-mate tests](/Users/edr/code/wt-d8cc9c0a-a281a/tests/test_scored_packer.py:70) cover the round-1 failures. |
| G4 | [reduce](/Users/edr/code/wt-d8cc9c0a-a281a/joulewise/scored_reduce.py:33) derives caps from tokens, keys windows by block and attempt, excludes voided windows, requires stages and complete item accounting, and carries typed terminal refusals, parent IDs, stage counts, and both digests. [Cap, window, completeness, and terminal tests](/Users/edr/code/wt-d8cc9c0a-a281a/tests/test_scored_reduce.py:31) exercise the defects. |
| G5 | [Registration structural tests](/Users/edr/code/wt-d8cc9c0a-a281a/tests/test_scored_registration.py:119), [roster record sweeps](/Users/edr/code/wt-d8cc9c0a-a281a/tests/test_scored_packer.py:148), and [row/window sweeps](/Users/edr/code/wt-d8cc9c0a-a281a/tests/test_scored_reduce.py:98) check required-key deletion, unknown keys, signatures without defaults, and absence of input-record `.get` or `setdefault`. Refusals use exported typed exceptions. |
| G6 | Packing retains cell balance, `idle_slot`, Williams ordering, spread, and worst-case single packing; reduction retains gross-only energy and the cap-bound label. The focused regressions and mutation results below cover these paths. |

### Registration field table

“Nullable” refers to pilot mode; every field name is required in both modes.

| Field | Type | Pilot nullable | Check |
|---|---|---:|---|
| `schema` | string | No | Exact v1 schema |
| `mode` | string | No | `pilot` or `registered` |
| `registration_id` | string | No | Nonempty |
| `plan_id` | string | No | Nonempty |
| `sizing_receipt_sha256` | SHA-256 string | Yes | Required when registered |
| `arm` | string | No | Present in arm map |
| `arm_to_family` | arm→string map | No | Family derived from selected arm |
| `role_to_model_id` | role→string map | No | Exact `8B`, `1.7B` roles; distinct IDs |
| `levels` | integer list | No | Exactly `[1,2,3,4,5]` |
| `merge_order` | integer-pair list | No | Exactly `[[5,4],[4,3],[1,2],[2,3]]` |
| `min_correct` | integer | No | Exactly 3 |
| `alpha` | number | No | Finite, `(0,1]` |
| `holm_m` | integer | No | Exactly 5 |
| `n_boot` | integer | No | Positive |
| `seed` | integer | No | Nonnegative |
| `floor_j` | number | No | Finite, nonnegative |
| `anchor_j` | number | No | Finite, nonnegative |
| `cap_tokens` | arm→integer map | No | Positive per arm |
| `cap_bound_fraction` | number | No | Exactly 0.20 |
| `block_size` | arm→integer map | No | Positive per arm |
| `n_per_level` | integer | No | Positive |
| `min_blocks_per_cell` | integer | No | Positive |
| `min_envelopes_per_cell` | integer | No | Positive |
| `envelope_s` | number | No | Positive; contains offset and interior |
| `offset_s` | number | No | Nonnegative |
| `interior_s` | number | No | Positive; exceeds guard |
| `guard_s` | number | No | Nonnegative |
| `pitch_s` | number | No | At least envelope length |
| `s_per_token_upper` | model→arm→number map | No | Positive; used in derived worst case |
| `prefill_s` | model→arm→number map | No | Nonnegative |
| `ceiling_s` | model→arm→number map | No | Between derived worst case and usable interior |
| `retry_stages` | string list | No | Exact five-stage vocabulary |
| `max_drift_lever_slots` | number | Yes | Nonnegative; budget formula when present |
| `delta_upper_j_per_block_slot` | number | Yes | Positive; budget formula when present |
| `budget_j` | number | Yes | Nonnegative; budget formula when present |
| `declared_sensitivities` | string list | No | Nonempty |
| `scorer_id` | string | No | Nonempty |
| `item_set_sha256` | SHA-256 string | No | Lowercase 64-character digest |

### Worked pilot example

The [pilot mapping fixture](/Users/edr/code/wt-d8cc9c0a-a281a/tests/test_scored_registration.py:12) sets `mode="pilot"`, receipt and drift-budget fields to `null`, five levels, ten items per level, block size 2, cap 100, upper decode rate 0.3 s/token, prefill 0, ceiling 30 s, and a 50 s usable interior. It produces registration digest `16e766ed…808d008`.

Packing yields `claim_ready=false`, roster SHA `c1ec61e9…8becdd`, and gaps `{1:0, 2:0, 3:0, 4:0, 5:0}`. For block `1.7B:on:1:0`, the requeue chain is `initial → whole_block → single_problem → single_retry → ceiling_violation`; its Level 1 executed gaps are `2.0 → 3.1333 → 3.4667 → 2.4` slots. The final reduced `1.7B/on/Level 1` cell has 9 measured attempts, 9 correct, 50 gross J, stage counts `{initial:8, single_problem:1, ceiling_violation:1}`, and a typed terminal refusal for `L1P0`. Its `roster_sha256` is `3fc42628…1f7684`.

## Verification notes

The mutation scripts used a `git archive HEAD` scratch copy, overlaid the six scoped files, collapsed each comparison and each `min`/`max` call to each operand one mutant at a time, and ran the named modules for each mutant.

| Module | Generated | Killed | Survived |
|---|---:|---:|---:|
| `scored_registration.py` | 90 | 90 | 0 |
| `scored_packer.py` | 152 | 152 | 0 |
| `scored_reduce.py` | 108 | 108 | 0 |

Final command: `python3 -B -m unittest tests.test_scored_registration tests.test_scored_packer tests.test_scored_reduce` → `Ran 13 tests in 1.501s`, `OK`. No commit was made.

## Residual risk

**Open rulings:** none blocks this infrastructure lane. The magistrate should confirm that AP-5M defines the sizing receipt’s `delta_upper` source and the canonical encoding behind `item_set_sha256`. The implementation treats those digests as opaque registered identities.

**Magistrate double-check:** review the derived `blocks_per_cell = ceil(n_per_level / block_size[arm])` in the drift formula, the reducer’s accepted `stop_reason` values (`stop`, `length`), and the runner’s obligation to supply each affected single’s own elapsed seconds.