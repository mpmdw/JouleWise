```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "A281a fails the delta re-audit: registered rosters can bypass both spread guards; the class-IV stop rule applies.",
  "workspace": {
    "base_requested": "c8d5d1f9ab4b52db385642d28b8d6d877cc63e50",
    "base_mode": "descendant",
    "head_start": "c0998fdb55fedc90213697dfaa61cf87a66e80e1",
    "head_end": "c0998fdb55fedc90213697dfaa61cf87a66e80e1",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 2, "should_fix": 1, "nit": 0},
    "findings": [
      {"id": "B1", "severity": "blocker", "title": "CLASS-IV: retry tails skip the one-block-per-cell-per-envelope guard"},
      {"id": "B2", "severity": "blocker", "title": "CLASS-IV: a registered roster can bypass the fixed five-block spread minimum"},
      {"id": "S1", "severity": "should_fix", "title": "Oversized integer inputs escape as untyped OverflowError"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_scored_registration tests.test_scored_packer tests.test_scored_reduce",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 13 tests in 1.525s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 13 tests in .*s[\\s\\S]*OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONPATH=. python3 -B /tmp/a281a_delta_findings.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["B1 registered True same_cell_envelopes [(12, ['1.7B:on:1:0:single:0', '1.7B:on:1:0:single:1'])]", "B2 registered True cell_blocks 1 cell_envelopes 1", "S1 prediction OverflowError int too large to convert to float"]},
      "expected": {"exit_code": 0, "tail_regex": "B1 registered True.*B2 registered True.*OverflowError"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B /tmp/a281a_delta_mutants.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["RESULT scored_registration.py generated 90 killed 90 survived 0 seconds 38.7", "RESULT scored_packer.py generated 152 killed 152 survived 0 seconds 195.6", "RESULT scored_reduce.py generated 108 killed 108 survived 0 seconds 214.8"]},
      "expected": {"exit_code": 0, "tail_regex": "generated 90 killed 90 survived 0[\\s\\S]*generated 152 killed 152 survived 0[\\s\\S]*generated 108 killed 108 survived 0"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONPATH=. python3 -B /tmp/a281a_delta_stress_m8.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["RESULT {'pilot_accepted': 160, 'chains': 264, 'registered_accepted': 160, 'same_cell_envelope': 160} max_wall_s 1.13 max_gap 12.546"]},
      "expected": {"exit_code": 0, "tail_regex": "pilot_accepted': 160.*registered_accepted': 160.*same_cell_envelope': 160"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONPATH=. python3 -B /tmp/a281a_delta_keys.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["COUNTS {'registration_drop': 38, 'registration_unknown': 1, 'row_drop': 13, 'row_unknown': 1, 'window_drop': 3, 'window_unknown': 1, 'roster_drop': 22, 'roster_unknown': 1, 'block_drop': 13, 'block_unknown': 1, 'envelope_drop': 7, 'envelope_unknown': 1, 'terminal_drop': 7, 'terminal_unknown': 1}", "FAILURES []"]},
      "expected": {"exit_code": 0, "tail_regex": "FAILURES \\[\\]"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "B1 and B2 meet the lane-local class-IV stop rule in record 26.",
      "needs": "Convene the prescribed consult; do not start round 3."
    }
  ]
}
```

### (a) Counterexample replays

Commands: `PYTHONPATH=. python3 -B /tmp/a281a_delta_probe.py`, `PYTHONPATH=. python3 -B /tmp/a281a_delta_findings.py`, and the named suite.

| Prior case | Observed at `c0998fdb` |
|---|---|
| Correct row at exactly the token cap, with no cap flag | `ReductionRefusal: truncated flag disagrees with token cap` |
| Missing `retry_stage` | `ReductionRefusal: item row keys differ` |
| Offset, interior, pitch, or derived ceiling incoherent | `RegistrationRefusal` in each probe |
| Registered drift gap after requeue | Level 1 gap changed `0.0 → 2.0`; `drift_exceeded[1] == True` |
| Incoming roster digest tamper | `PackingRefusal: ... digest mismatch` |
| Innocent envelope mate | Bad item became `ceiling_violation`; mate remained `single_problem` |
| Whole-block attempt-window collision | Attempt 0’s 10,000 J voided window was excluded; cell gross remained 50 J. Duplicate window refused. |
| Failed prediction above derived worst case | `PackingRefusal: ... derived worst case below failed prediction` |
| Split and terminal accounting | Typed terminal refusal for `L1P0`; sibling retained its parent ID |
| Partial level set or oversized initial block | `PackingRefusal` for each |
| Initial balance, idle slot, gross-only reduction, cap-bound label | Five zero measured-cell gaps; one idle slot; 50 J gross; three cap hits yielded fraction `0.3` and `cap_bound=True` |
| Former parity mutant, 12 items at block size 2 | 12 envelopes, zero idle slots, zero gaps |

### (b) File-level operand-collapse sweep

A `git archive HEAD` copy under `/tmp` received one comparison or `min`/`max` operand cut at a time. The AST-unparsed baseline also passed the named suite.

| Module | Generated | Killed | Survived |
|---|---:|---:|---:|
| `scored_registration.py` | 90 | 90 | 0 |
| `scored_packer.py` | 152 | 152 | 0 |
| `scored_reduce.py` | 108 | 108 | 0 |

### (c) Seeded stress

Seed `281093`: 320 accepted registrations and rosters, split evenly between pilot and registered mode. The sweep sampled level sizes 5–40, valid block sizes 1–6, speed ratios 1:1 through 1:8, and 264 random requeue chains. It retained the ruled five-block and five-envelope minima.

| Lost or duplicated items | Envelopes over capacity | Same-cell block collisions | Repeated-input SHA mismatch | Maximum pack wall time |
|---:|---:|---:|---:|---:|
| 0 | 0 | **160** | 0 | 1.13 s |

The 160 count is violating envelopes, not distinct rosters. The largest recorded executed gap was 12.546 slots under a deliberately loose registered drift limit.

### (d) Drop-key and unknown-key probes

| Record | Dropped required keys refused | Added unknown key refused |
|---|---:|---:|
| Registration | 38/38 | Yes |
| Item row | 13/13 | Yes |
| Block window | 3/3 | Yes |
| Roster | 22/22 | Yes |
| Roster block | 13/13 | Yes |
| Envelope | 7/7 | Yes |
| Terminal refusal | 7/7 | Yes |

For `arm_to_family`, `role_to_model_id`, `cap_tokens`, `block_size`, `s_per_token_upper`, `prefill_s`, and `ceiling_s`, a missing required arm or model key refused **at `Registration.from_mapping`**, including missing keys inside each model’s per-arm map. Unknown nested keys also refused. A separate prediction-map probe found that missing required model or item predictions refuse at `pack`; extra model and item predictions are ignored with an unchanged roster SHA. Exact prediction-map domain was not among G5’s enumerated record schemas.

### Same-signature statement

| Signature | Recurred? | Finding |
|---|---|---|
| Decision semantics | No decision implementation in this lane | None |
| Pairing or item accounting broken by retries or splits | No loss or duplication in the executed stress chains | None |
| Balance calculated from labels instead of measured cells | No; gaps were computed from scheduled measured blocks | None |
| Silent defaults or a guard skipped on a path | **Yes** | **B1, B2** |
| Surviving operand-collapse mutants | No; 350/350 killed | None |

## Findings

**B1 — Blocker, CLASS-IV.** The initial arranger enforces one block per cell per envelope, but the retry append path at [scored_packer.py](/Users/edr/code/wt-d8cc9c0a-pure-review/joulewise/scored_packer.py:273) packs two split blocks from `(1.7B, on, Level 1)` into envelope 12. `PYTHONPATH=. python3 -B /tmp/a281a_delta_findings.py` printed `registered True same_cell_envelopes [(12, ['1.7B:on:1:0:single:0', '1.7B:on:1:0:single:1'])]`. This skips P1/M8’s spread guard on the retry path while retaining `claim_ready=True`. The M12 permission to pack several singles per envelope needs a ruling on how it coexists with G6’s instruction to retain M8.

**B2 — Blocker, CLASS-IV.** [Registration.from_mapping](/Users/edr/code/wt-d8cc9c0a-pure-review/joulewise/scored_registration.py:127) accepts `min_blocks_per_cell=1` and `min_envelopes_per_cell=1`; [pack](/Users/edr/code/wt-d8cc9c0a-pure-review/joulewise/scored_packer.py:235) then uses those values as the entire spread guard. P1/M8 requires at least five of each. The same command printed `B2 registered True cell_blocks 1 cell_envelopes 1` for a five-item, block-size-six registered roster.

**S1 — Should fix.** Numeric checks in [registration](/Users/edr/code/wt-d8cc9c0a-pure-review/joulewise/scored_registration.py:51), [packer](/Users/edr/code/wt-d8cc9c0a-pure-review/joulewise/scored_packer.py:34), and [reducer](/Users/edr/code/wt-d8cc9c0a-pure-review/joulewise/scored_reduce.py:27) call `math.isfinite` on arbitrarily large Python integers. The findings command supplied `10**400` as `floor_j`, predicted seconds, and `gross_j`; each escaped as `OverflowError: int too large to convert to float`, contrary to G5’s typed-refusal requirement.

## Residual risk

This pure-module audit did not exercise a scored-night runner or live capture. The worktree remained clean. Because B1 and B2 are class-IV findings, record 26’s lane stop calls for a consult rather than a third fix round.