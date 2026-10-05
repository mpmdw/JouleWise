```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Production sizing sources updated; the 335-second frequency allowance passes, but writer integration and code-proven T-0 bounds remain blocked.",
  "workspace": {
    "base_requested": "bda1c180cf156ecedcbe01a6010390dcd724c8cc",
    "base_mode": "exact",
    "head_start": "bda1c180cf156ecedcbe01a6010390dcd724c8cc",
    "head_end": "bda1c180cf156ecedcbe01a6010390dcd724c8cc",
    "upstream_end": "e7d13a1706d6352e0b3d9624dcf4c897671393da",
    "branch": "lane/2026-10-05-b4-sizing2"
  },
  "pathspec": [
    "configs/campaigns/v5_qualification_25g83/sizing_allowances.json",
    "configs/campaigns/v5_qualification_25g83/sizing_sources/sizing_source_v2.json",
    "tests/test_v5_qualification_plan.py",
    "tests/test_v5_block4_clock.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-sz PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_v5_qualification_plan tests.test_v5_block4_clock tests.test_v5_block4_x6",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 79 tests in 20.053s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?s)Ran 79 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "TMPDIR=/tmp/dd5-sz PYTHONDONTWRITEBYTECODE=1 python3 /tmp/dd5-sz/replay_sizing.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 3,
        "tail": ["SIZING_REFUSED: stream_omits_guard_or_retry"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "window_max_s"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "TMPDIR=/tmp/dd5-sz PYTHONDONTWRITEBYTECODE=1 python3 /tmp/dd5-sz/check_sizing_sources.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "SOURCES_OK: 69 source-bound allowances; 67 authenticated archive timing sources; 23 configs; fixture unchanged",
          "ARITHMETIC_OK: span=25434 window=28140 latest=2706 emergency=28440 courier=28740 deadman=ceil_minute(t0+32040)",
          "GATE_OK: T_stream_max=335; stated -3.17 ppm bound=4.84570 ms margin=0.15430 ms; limit=973/268 ppm",
          "RAW_FREQUENCY_LIMIT: 237934 118967/32768"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?s)SOURCES_OK:.*ARITHMETIC_OK:.*GATE_OK:"
      }
    },
    {
      "id": "V4",
      "kind": "lint",
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
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "Necessary writer integration is outside WRITE_SCOPE. scripts/write_v5_qualification_plan.py:183-184 includes the separate cooldown in main-stream coverage and refuses the new file. Lines 179-188 lack a stream minimum check; line 147 lacks a pack_t0 band check. No out-of-scope file was edited.",
      "needs": "X7/X9 must correct stream coverage, enforce the applicable 60-second minimum and approved T-0 band, then rerun V2."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "X=3300 is PROVISIONAL. Its conditional design band is 3180-3480 seconds, with 120 seconds of lead margin and 180 seconds of conservative G4 margin. No code-proven admissible band exists: capture_t0_step.py:634 leaves quiet/ledger commands unbounded; run_night.py:3738 permits 3600 seconds for captures alone, and 3600+120 seconds of author allowance exceeds G4's 3600-second ceiling. Writer line 585 supplies a prerequisite boundary; run_night.py:3870 executes captures at t0.",
      "needs": "Approve and enforce aggregate capture/author/verification budgets and the pre-t0 schedule before treating 3300 as an admissible operational value."
    },
    {
      "id": "F3",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Ruling 76 D.2 and design registration section 4 require two distinct dwells. run_night.py:3665-3687 instead reuses the T-0 dwell. The source retains a separate 2700-second pre-chain cap outside the span under the controlling ruling.",
      "needs": "X8 must implement the distinct sealed pre-chain dwell, or the lead must change the ruling and recompute the window."
    },
    {
      "id": "F4",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Member and calibration anchor-bearing streams exceed 60 seconds with stated margins. A literal requirement covering every native sampler also fails: cooldown subwindows and the separate post-run sentinel are short helper captures.",
      "needs": "Confirm that memo 1.8's minimum applies to anchor-bearing streams; otherwise specify the required helper-stream changes."
    },
    {
      "id": "F5",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Auxiliary timing remains the approved small-model proxy from ruling 76 A.3. These are prospective allowances, not hard inference-latency guarantees or live s1 validation.",
      "needs": ""
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "scripts/write_v5_qualification_plan.py",
      "scripts/run_night.py",
      "scripts/capture_t0_step.py"
    ],
    "reason": "Required integration belongs to the other lanes and lies outside this worker's exhaustive allowlist.",
    "blocked_work": "Successful production sizing replay and an operationally proven T-0 lead-time band.",
    "minimal_change": "Exclude separate cooldown from main-stream coverage, enforce stream minimum and approved lead-time bounds, schedule bounded T-0 work before t0, and implement the ruled second dwell."
  }
}
```

## Change

Repointed all **69 allowances**, including the clock source, to the production derivation. It authenticates **67 archive timing sources and 23 regenerated configs**. The test fixture remains unchanged. Changes are uncommitted; nothing was pushed.

In the tables, **S** means [the production derivation](/Users/edr/code/JouleWise-wt-dd5-sz/configs/campaigns/v5_qualification_25g83/sizing_sources/sizing_source_v2.json), SHA-256:

`3ea0901cd78779234f3782d52e78cd14ce8ad2fdea49b6067a2947e8fa668d4d`

Each source cell is its JSON pointer in S; S contains the underlying production and archive locators.

| Component | Old s → new s | Source pointer in S | Derivation |
|---|---:|---|---|
| Load, small / large | 3 / 6 → unchanged | `/members/{small,large}/load` | Ceiling of 1.5 × observed prepare maximum |
| Warmup, small / large | 10 / 16 → unchanged | `/members/{small,large}/warmup` | Ceiling of 1.5 × observed maximum |
| Prefill, small / large | 2 / 9 → unchanged | `/members/{small,large}/prefill` | Conservative 4096-token timing proxy |
| Forced decode, small / large | 5 / 13 → unchanged | `/members/{small,large}/forced_decode` | Ceiling of 1.5 × 512-token maximum, plus 1 s |
| Cooldown/member | 300 → 300 | `/members/small/cooldown` | Production cap; separate sampler |
| Idle admission/member | 275 → 275 | `/members/small/idle_admission` | Two 110 s attempts + three 15 s guards + 10 s sentinel |
| Sampler startup/member | 0 → 15 | `/derivations/stream_max/native_sampler_overhead/startup_s` | Production readiness timeout |
| Sampler wind-down/member | 0 → 17 | `/derivations/stream_max/native_sampler_overhead/winddown_s` | `ceil(1 + 5 + 0.2 + 0.25 + 10)` |
| **Full `E_small`** | **595 → 627** | `/totals/E_small_full` | Legacy subtotal + 32 s sampler custody |
| **Full `E_large`** | **619 → 651** | `/totals/E_large_full` | Legacy subtotal + 32 s sampler custody |
| Full auxiliary member | 595 → 627 | `/totals/E_small_full` | Approved small-model proxy |
| `E_ABBA` | 2428 → 2556 | `/totals/E_ABBA_full` | `2·627 + 2·651` |
| NEG-8 collection | 7140 → 7524 | `/totals/gamma_bound_collection_full` | `12·627` |
| Start references | 1785 → 1881 | `/totals/gamma_reference_start_full` | `3·627` |
| Midpoint reference | 595 → 627 | `/totals/gamma_reference_decode_midpoint_full` | One auxiliary member |
| End references | 1785 → 1881 | `/totals/gamma_reference_end_full` | `3·627` |
| Bound derivation | 60 → 60 | `/auxiliary/gamma-bound-derivation` | Approved allocation |
| **Full bound and references** | **11365 → 11973** | `/totals/T_bound_and_references_full` | `19·627 + 60` |
| **`T_pack_t0`** | **360 → 3300, provisional** | `/fixed/pack_t0` | Conditional dwell/capture/author/verification budget |
| Fixed settles | 3700 → 3700 | `/fixed/fixed_settles` | Six 600 s settles + five 20 s countdowns |
| Pre/post calibration | 770 → 770 | `/fixed/pre_post_calibration` | `2·(240+20+5+120)` |
| Legacy custody | 2835 → 2835 | `/derivations/stage_custody/legacy_custody_s` | Existing approved allocations |
| Writer custody field | 2835 → 3571 | `/fixed/stage_custody` | Legacy custody + `23·32` sampler custody |
| Terminal shutdown | 300 → 300 | `/fixed/terminal_shutdown` | STOP/shell-exit allocation |
| Post-quiet backups/close-out/OFF | 420 → 420 | `/totals/post_quiet_backup_close_off_s` | Outside quiet span |
| Small / auxiliary stream | 592 → 314 | `/streams/small` | `15 + (275−10) + 10+2+5 + 17` |
| Large stream / **`T_stream_max`** | **613 → 335** | `/totals/T_stream_max` | `15 + (275−10) + 16+9+13 + 17` |
| Calibration stream allowance | 240 → 240 | `/streams/bracket` | Observed maximum 196.843 s + margin |
| **Programmed span** | **21758 → 25434** | `/totals/NIGHT_PROGRAMMED_SPAN_S_s1` | Formula below |
| **Window maximum** | **24480 → 28140** | `/totals/WINDOW_MAX_S_s1` | `60·ceil((25434+2700)/60)` |
| Latest chain start, relative to `t0` | 2722 → 2706 | `/totals/latest_start_offset_s` | Window − span |
| Emergency deadline, relative to `t0` | 24780 → 28440 | `/derivations/deadlines/emergency_shutdown_offset_s` | Window + 300 |
| Courier deadline, relative to `t0` | 25080 → 28740 | `/derivations/deadlines/courier_deadline_offset_s` | Window + 600 |
| Dead-man, minute-aligned `t0` | 28380 → 32040 | `/derivations/deadlines/deadman_unrounded_offset_s` | Otherwise `ceil_to_minute(t0+32040)` |

The full-envelope accounting is:

```text
3300 + 3700 + 770 + 11973 + 2556 + 2835 + 300 = 25434 s
```

For compatibility with the writer’s six member components, the allowance file charges the same **736 s** of sampler custody through its fixed custody field:

```text
3300 + 3700 + 770 + 11365 + 2428 + 3571 + 300 = 25434 s
```

These are equivalent accounts; the sampler custody is charged once.

| Control component | Old s → new s | Source pointer in S | Basis |
|---|---:|---|---|
| ARM capability horizon | 300 → 300 | `/controls/arm_capability_horizon_s` | Earlier of evaluation + 300 and evidence deadlines |
| Volatile horizon | 1200 → 1200 | `/controls/volatile_horizon_s` | Evidence origin |
| Nonvolatile horizon | 21600 → 21600 | `/controls/nonvolatile_horizon_s` | Not the control wait |
| Absence-check offset | 120 → 120 | `/controls/check_offset_s` | After controlling expiry |
| Shutdown offset | 420 → 420 | `/controls/shutdown_offset_s` | Same origin |
| Courier offset | 720 → 720 | `/controls/courier_offset_s` | Same origin |
| Dead-man offset | 4020 → 4020 | `/controls/deadman_offset_s` | Rounded to minute by recipe |

Idle admission already used idle-75 archive evidence in record 44. The regenerated configs request **750 records**; the 40 comparable idle slices contain **97.667–100.303 s** of native elapsed time. The largest observed admission attempt is **103.554 s**, leaving **6.446 s** below its 110 s allowance. Adding another 45 seconds per attempt would count the regeneration twice.

Cooldown separation is proven by the main sampler stop at [controller.py:1607](/Users/edr/code/JouleWise-wt-dd5-sz/joulewise/controller.py:1607), a separately resolved cooldown adapter at [run_campaign.py:4299](/Users/edr/code/JouleWise-wt-dd5-sz/scripts/run_campaign.py:4299), and its independent idle capture at [controller.py:2847](/Users/edr/code/JouleWise-wt-dd5-sz/joulewise/controller.py:2847).

The frequency evaluation is:

```text
3.60 + 0.10 + (3.17 + 0.25)·335/1000 = 4.84570 ms
margin = 0.15430 ms
largest mathematical |f| = 1300/335 − 0.25 = 3.630597015 ppm
```

The largest representable passing kernel word is **237934**, or **3.630584717 ppm**; the next word fails. The old 613 s allowance gives **5.79646 ms**. **X3 F2’s inequality refusal clears**, while the writer’s separate coverage refusal remains.

For the lower bound, 750 records give a nominal endpoint span of **74.9 s**, a **14.9 s** margin. The smallest comparable idle endpoint span is **97.545728 s**, a **37.545728 s** margin before warmup or measurement. Calibration’s programmed capture is **196.703125 s**, a **136.703125 s** margin. F4 records the unresolved literal treatment of short helper captures.

## Verification notes

The baseline had two roster-fixture errors using retired auxiliary paths. Those fixtures now follow the regenerated `_v5` paths.

The production sizing path authenticates the real roster, then refuses `stream_omits_guard_or_retry` at [writer.py:183](/Users/edr/code/JouleWise-wt-dd5-sz/scripts/write_v5_qualification_plan.py:183). Production writer code was left untouched.

**T-0 remains provisional.** With OFF settling overlapping the subsequent dwell and admission at the author boundary, the proposed design budgets give:

```text
minimum X = 2700 + 240 captures + 120 author + 120 verification = 3180 s
maximum X = 3600 − 120 author = 3480 s
candidate X = 3300 s: 120 s lead margin; 180 s conservative G4 margin
```

The current code does not enforce those aggregate budgets. Its permitted capture timeout alone gives `3600 + 120 = 3720 > 3600`, so there is **no code-proven admissible X** today.

The outside **2700 s cap remains required by addendum D’s second, sealed pre-chain dwell**. The current driver’s reuse conflicts with that ruling. If the lead removes the second dwell, the alternative window is **25440 s**, with latest-start offset **6 s**.

The full canonical suite was not run for this bounded sizing/configuration and test-fixture task. No live measurement was performed.

## Residual risk

The source is explicitly **PROVISIONAL and not arm-ready**. The next step is for X7/X9 to resolve F1/F2, X8 or the lead to resolve F3, and the lead to confirm F4’s stream scope, then rerun the production sizing replay.