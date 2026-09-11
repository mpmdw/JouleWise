```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Reject the §5C-row candidate: D-134 has no post-launch lifecycle; use a dedicated append-only collection-margin receipt referenced by the freeze manifest.",
  "workspace": {
    "base_requested": "origin/main and integration/5c-readiness",
    "base_mode": "informational",
    "head_start": "a6f235834975117120e289408e187d2bdc965309",
    "head_end": "a6f235834975117120e289408e187d2bdc965309",
    "upstream_end": "a6f235834975117120e289408e187d2bdc965309",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "recommendation": "Add a dedicated, canonical, append-only comparative-cell window-margin receipt generated immediately after finalized post-calibration and before backup/extraction; point to it from the freeze manifest and close-out checklist, but do not add it to D-134 arm readiness.",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The proposed collection-time readiness row has no valid D-134 lifecycle",
        "text": "The integration branch permits only FREEZE_AND_ARM and ARM_ONLY rows. Both are evaluated before physical launch; the ARM receipt is then atomically consumed. A cell duration cannot exist then. Making the row required would refuse every arm, while evaluating it after collection would mutate the semantics of an already-consumed authorization receipt."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "Preserve the original D-124 margin and the independent cadence evidence as separate fields",
        "text": "The dead FCM inventory computed min(duration_s - 2*B_operative_s). WO-4's independent risk is sample support: at least three overlapping intervals and the reducer's 2.0 cadence-ratio threshold. A replacement must record both; neither scalar is a substitute for the other."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "title": "Silence or an explicit drop is not supportable on the current record",
        "text": "D-133 explicitly kept items (1) and (3) live, and WO-4 found 37/50 1.5B p128 windows below the three-interval requirement. The p256 population is unmeasured. Dropping the obligation would discard the only prospective check precisely where the evidence says extrapolation is unsafe."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git rev-parse origin/main && git rev-parse integration/5c-readiness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## main...origin/main",
          "a6f235834975117120e289408e187d2bdc965309",
          "a6f235834975117120e289408e187d2bdc965309",
          "5a80e396238336e6a321e20dcb244b32df23d02c"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "5a80e396238336e6a321e20dcb244b32df23d02c$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git show integration/5c-readiness:configs/arm_readiness/d117_row_registry_v1.json | jq -r '([.rows[].evaluation_phase] | unique | join(\",\")), (.rows | length), ([.rows[].row_id | select(test(\"collection\"; \"i\"))] | length)'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "ARM_ONLY,FREEZE_AND_ARM",
          "35",
          "0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "ARM_ONLY,FREEZE_AND_ARM\\n35\\n0$"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git show integration/5c-readiness:joulewise/arm_readiness.py | sed -n '132,148p'; git show integration/5c-readiness:scripts/generate_arm_readiness.py | rg -n 'add_parser\\(|choices='",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "EVALUATION_PHASES = frozenset({\"FREEZE_AND_ARM\", \"ARM_ONLY\"})",
          "33:    freeze = subparsers.add_parser(\"freeze\")",
          "36:    dry_run = subparsers.add_parser(\"dry-run\")",
          "42:    arm = subparsers.add_parser(\"arm\")",
          "47:    verify = subparsers.add_parser(\"verify\")",
          "51:    consume = subparsers.add_parser(\"consume\")"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "51:    consume = subparsers.add_parser\\(\"consume\"\\)$"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git show integration/5c-readiness:joulewise/reduce.py | sed -n '112,120p'; git show integration/5c-readiness:joulewise/reduce.py | sed -n '1024,1036p'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "MIN_PHASE_SAMPLES = 3",
          "SHORT_WINDOW_CADENCE_RATIO_MIN = 2.0",
          "\"window_duration_s\": window.duration_s,",
          "\"in_window_sample_count\": sample_count,",
          "\"cadence_ratio\": cadence_ratio,",
          "\"cadence_ratio_min\": cadence_ratio_min,"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\"cadence_ratio_min\": cadence_ratio_min,"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "A receipt can expose insufficient temporal resolution but cannot repair the collected evidence; an inadequate p256 result still requires recollection, claim demotion, or a separately ruled disposition.",
      "needs": ""
    }
  ]
}
```

## Findings

### F1 — Blocker: reject the magistrate’s §5C-row candidate

There is no existing collection-time registry class on `integration/5c-readiness`. The registry has 35 rows and exactly two phases:

- `FREEZE_AND_ARM`
- `ARM_ONLY`

Both precede physical launch. The final ARM receipt is then consumed atomically before the frozen foreground command runs. The proposed p256 predicate therefore asks a pre-launch authorization artifact to derive facts from future bundle bytes.

That cannot be repaired by merely adding `COLLECTION_TIME` to the enum:

- If the row is required for GAMMA at arm, missing future evidence correctly becomes `REFUSE`, so GAMMA can never launch.
- If it is ignored at arm and evaluated afterward, it is not part of the authoritative required-row evaluation and does not gate anything.
- If the ARM receipt is amended afterward, the two-stage append-only authorization contract and consumed-receipt identity are broken.
- D-134 row records contain verdicts and evidence IDs, not scalar results. The values would have to live in another receipt anyway.

D-134’s “sole row authority” is authority for arm readiness, not a mandate to turn every later workflow obligation into an arm row. The candidate mistakes a scoped registry for a universal lifecycle registry.

The closest existing machinery is `summary_metrics.json.window_evidence_precheck.phase`: the reducer already derives duration, overlapping sample count, observed gaps, cadence ratio, and the 2.0 threshold. It is useful input, but it is not a cell-level registry row, does not aggregate the registered comparative-cell census, and does not record the D-124-style minimum margin. The obligation is therefore not already discharged.

### F2 — Should fix: use a dedicated collection-margin receipt

Recommended surface:

- `joulewise/window_duration_margins.py`: deterministic derivation and closed receipt schema.
- `scripts/record_window_duration_margins.py`: operator-free conclusion path; accept roots/pack identity, never cell IDs, margins, statuses, or output paths.
- `tests/test_window_duration_margins.py`: census, mutation, missing-member, malformed-window, unknown-bound, p256, determinism, and refusal tests.
- `docs/phase_2/three_night_freeze_manifest.md`: a pointer item analogous to D-8′.
- `docs/phase_2/window_runbook.md` §12: record the receipt path and SHA separately from mint/extraction outputs.

Generate the receipt immediately after the post-calibration slot is finalized and before backup/extraction. Pack freeze gates on the mechanism, schema, registered-cell inventory, and deterministic output namespace; collection close-out gates on the resulting receipt.

For each cell, the receipt should derive and preserve at least:

- `cell_id`, metric, membership digest, member count;
- authenticated `B_operative`;
- minimum phase-window duration and its bundle ID;
- `min_duration_minus_2b_operative_s`;
- `min_duration_to_2b_operative_ratio`;
- minimum overlapping-power-interval count;
- `min_sample_count_margin = count − 3`;
- recorded reducer cadence ratio/threshold where derivable;
- SHA-256 of every authoritative input stream.

The original required margin remains:

`min_member(duration_s − 2 × B_operative_s)`

The producer should obtain:

- Cell census and member IDs from the final pack-pinned extraction specs and GAMMA `analysis_manifest_v3.json`. This automatically includes the Q8 p256 cells once their final registration lands; no hard-coded list.
- Phase start/end from each bundle’s validated `events.jsonl`.
- `B_operative` through `AuthenticatedConsumptionSession`, which authenticates the ledger snapshot and pre/post calibration primary evidence rather than accepting a scalar.
- Overlap count and cadence evidence from `raw/powermetrics.plist` replayed to, and checked against, `power_trace.csv`.
- `summary_metrics.json.window_evidence_precheck` only as a cross-check, never as an operator-copy surface.

Receipt `PASS` should mean “every registered cell and member was uniquely found and every required value was derived from authenticated bytes.” It should not silently mean that all margins were positive: D-133 did not rule a new acceptance threshold. Missing membership, non-unique phase windows, failed raw-to-trace replay, unavailable `B_operative`, nonfinite arithmetic, or an unrecordable minimum must produce `REFUSE`, never UNKNOWN.

This beats the alternatives:

- It is collection-time and pre-mint, so it survives a later mint refusal or delay.
- It preserves the D-134 authorization boundary.
- It turns the checklist into a digest-bound artifact instead of an operator-entered number.
- It keeps the scientific observation visible even when the worst-case estimator is used.
- The mint may reuse the same library, but mint success cannot be the first evidence that the check happened.

### F3 — Should fix: do not record a drop

A drop is indefensible without reversing the explicit item-level disposition. D-133 removed the estimator, not the observed short-window regime. WO-4’s 37/50 result is direct evidence that temporal support can be inadequate on the 1.5B stack, while p256 currently has no measurement evidence. “Likely longer” is exactly the unsupported inference item (3) forbids.

Smallest implementing work order:

> **WO-COLLECTION-MARGIN-01 — comparative-cell window-margin receipt.** Add a deterministic, append-only receipt generated after finalized post-calibration and before backup/extraction. Derive the complete comparative-cell census from the final pack; derive each member’s phase duration from validated event bytes, `B_operative` from the authenticated bracket session, and sampler support from replay-verified power intervals. Record each cell’s minimum `duration − 2·B_operative`, ratio, attaining member, minimum overlap count, and sample-count margin. Refuse incomplete, ambiguous, nonfinite, or unauthenticated evidence; accept no operator-entered conclusions. Add the freeze-manifest pointer, §12 path/SHA recording, and focused mutation/census tests. Do not modify the D-134 row registry.

## Residual risk

A positive `duration − 2·B_operative` does not prove three sampled intervals overlap the phase window; phase alignment and irregular cadence remain distinct. Conversely, the receipt cannot make a two-interval window identifiable. It can only expose the condition promptly so the claim path refuses, recollection occurs, or the magistrate records an explicit evidentiary demotion.