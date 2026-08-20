```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Complete mechanical-gate design: use a new scheduler core plus enforced arm/launch bindings; do not place it in run_campaign.",
  "workspace": {
    "base_requested": "5bd7acf",
    "base_mode": "informational",
    "head_start": "60ddb03a903d1e005190c966960fb091ed4f0e53",
    "head_end": "60ddb03a903d1e005190c966960fb091ed4f0e53",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "No scheduler exists at 5bd7acf, and run_campaign contains no minimum-fuse gate.",
        "evidence": "Target inspection found no scheduler files, no fuse/span terms in scripts/run_campaign.py, and only the post-arm R1 temporal-budget check in arm_readiness."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "The authoritative D-149 form cannot presently custody r3 B-3 timing measurements.",
        "evidence": "The template has no T-0 monotonic stamp, arm monotonic stamp, consumption reference, or defined one-sample p99 representation."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "title": "B-22 cure-presence and authorization-binding schemas need the D-144 magistrate decisions required by r5 V-6.",
        "evidence": "Current margins validation validates a receipt alone; only the recorder and module reference it, so no frozen-pack-aware claim consumer or scheduler admission proof exists."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git show 5bd7acf:scripts/run_campaign.py | rg -n -i 'minimum.?fuse|remaining.{0,40}fuse|projected.{0,40}(span|duration)|span.{0,40}margin|arm_to_consume' || true",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["No matching scheduler/minimum-fuse terms at 5bd7acf."]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "No matching scheduler/minimum-fuse terms.*"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git grep -l 'validate_window_duration_margins_receipt\\|window_duration_margins' 5bd7acf -- joulewise scripts",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["5bd7acf:joulewise/window_duration_margins.py", "5bd7acf:scripts/record_window_duration_margins.py"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "window_duration_margins"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_arm_readiness.R1LifecycleTests.test_temporal_budget_requires_full_consume_horizon tests.test_window_duration_margins.WindowDurationMarginsTests.test_unrecordable_minimum_refuses_without_output",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FileNotFoundError: [Errno 2] No usable temporary directory found"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    }
  ],
  "flags": [
    {
      "id": "FL1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The checkout is 60ddb03, an ancestor of requested 5bd7acf; target-code claims were inspected with git show.",
      "needs": "Apply the eventual design at the ruled head."
    },
    {
      "id": "FL2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Read-only sandbox provides no writable temporary directory, so the focused unittest could not import its temp-dependent module.",
      "needs": "Rerun focused tests in a writable implementation worktree."
    }
  ]
}
```

## Findings

### F1 — proposed gate architecture

Put the logic in a new pure module, `joulewise/window_scheduler_gates.py`, with a thin CLI, `scripts/evaluate_window_scheduler_gates.py`. Do not add it to `scripts/run_campaign.py`: at the ruled head it has no fuse-related surface, and it runs after the launch path. The existing minimum-fuse check is already in `joulewise.arm_readiness.validate_r1_temporal_budget()` and is called during arm issuance, not campaign scheduling (`joulewise/arm_readiness.py:3299-3340`, `:6151-6159`).

Required sequence:

```text
pre-arm admission ──PASS──> issue arm receipt
      │                             │
      REFUSE                         ▼
  custody refusal           pre-consume D-149 evaluation
                                    │
                             GO receipt + authorization
                                    │
                              launch_window consumes
                                    │
                        shakedown timing receipt closes
                                    │
                     claim admission checks halt bounds
```

The module should return an append-only `window_scheduler_gate_receipt` with:

- `status: PASS|REFUSE`, `authorization: PERMIT|NO_GO`, phase, window class, pack identity, reviewed-main proof, boot UUID, and evaluation monotonic timestamp.
- Canonical, sorted `checks` and `refusals`; every input is a path+SHA-256 reference or a live-probe transcript hash.
- On refusal, write a custody receipt and do not issue an arm or call `launch_window`.
- On pass, bind the receipt hash into the arm path and require a matching final authorization receipt in `scripts/launch_window.py` before consumption. Otherwise a direct CLI call bypasses the scheduler.

Use the existing refusal record shape—`type`, `code`, `row_id`, `evidence_id`—and closed-vocabulary enforcement (`joulewise/arm_readiness.py:338`, `:941-959`, `:1434-1448`). Reuse existing codes where applicable:

- `TEMPORAL_BUDGET`’s code/type from the installed lifecycle registry for minimum fuse.
- `readiness_git_tree_dirty` and `readiness_reviewed_main_mismatch` for reviewed-main.
- `readiness_record_expired` for a changed boot UUID and `readiness_io_error` for an unreadable boot probe.

New scheduler-only codes must be closed in the new scheduler receipt contract during the required D-144 ruling—not emitted ad hoc.

### Gate inventory

| Gate | Inputs and rule | Refusal / test pins |
|---|---|---|
| Minimum fuse | Earliest valid `TIME_BOUND` evidence deadline, live monotonic time, and the installed registry’s `arm_to_consume_budget_ns`. Require remaining fuse `>=` that value. V5 fixes it at 300 s; it is the arm→consume projection plus the ruled one-minute margin, not a multi-hour capture-window duration. | Use the registry’s `TEMPORAL_BUDGET` code/type. Pin exact-boundary pass, one-nanosecond-short refusal, missing deadline refusal, and prove the scheduler invokes the existing arm check too. |
| Shakedown halt bounds | A custodied shakedown timing record: T-0 monotonic stamp, arm monotonic stamp, consumption monotonic stamp, pack/head/boot bindings. Before every claim admission require `T-0→arm <= 900 s` and observed p99 `arm→consume <= 240 s`; otherwise latch campaign halt. | New closed scheduler roles: missing/malformed measurement, T0-arm exceeded, arm-consume p99 exceeded. Pin 900 s/240 s inclusive pass and +1 ns refusal; claims refuse without a valid, exact-family shakedown record. Shakedown itself is exempt because it creates the measurement. |
| B-22 claim admission | Claim only: verify a cured, frozen-pack-aware margins consumer is present at the reviewed head and is bound to the selected `_v4` pack/registry. It must reject the known SHA-repaired truncated-cell fixture. | New closed B-22-cure-unavailable role. Pin shakedown pass without cure, claim refusal without cure, wrong-pack refusal, truncated-receipt refusal, and refusal to promote any shakedown close-out later. |
| `reviewed_main` fail-early | Fresh `reviewed_main(pack_root)`: clean and `exact_match == true` before pre-arm admission. | Existing `readiness_git_tree_dirty` or `readiness_reviewed_main_mismatch`. Pin dirty, local-main divergence, origin-main divergence, and exact pass; assert no arm namespace mutation on failure. The existing predicate is at `joulewise/arm_readiness.py:3652-3674`. |
| Boot UUID pin | T-0 GO boot UUID, arm receipt boot UUID, and a fresh `sysctl kern.bootsessionuuid` probe must be identical before arm and before consume. | Existing `readiness_record_expired` on mismatch; `readiness_io_error` if unprobeable. Pin all-equal pass, each pairwise mismatch, and probe failure. |
| D-149 C1–C5 | C1: custodied council verdict plus three form conclusions. C2: PASS/GO arm receipt and recomputed freshness. C3: attached census/quiescence outputs. C4: boot and clock-off evidence. C5: scheduler lane state proves no prior refusal/retry and records D-078 binding. | One closed scheduler role per failed C-condition, plus malformed/missing evidence. Pin five single-condition refusals, all-pass canonical GO receipt, refusal receipt before launch, and second-arm refusal after a lane refusal. |

The fuse meaning is important: r3 expressly says `arm_to_consume_budget_ns` is the minimum remaining T-0 evidence life at arm, not the measured arm→consume gap. V5 fixes the 300 s budget and 240 s p99 with 60 s margin (`custody-staging/MAGISTRATE-RULING.md:95-105`). The existing arm receipt caps validity at the lesser of the capability horizon and evidence expiries (`joulewise/arm_readiness.py:6230-6242`).

### F2 — timing receipt gap

r3 requires the first shakedown GO receipt to record both gaps and mechanically halt before any claim window if either fails (`custody-staging/MAGISTRATE-RULING-r3.md:57-69`). The present D-149 template has neither monotonic timing fields nor a consumption reference (`docs/process/d149-go-receipt-template.md:10-39`).

The co-design should add immutable fields to the structured GO/timing receipt:

- `t0_monotonic_ns`
- `armed_at_monotonic_ns`
- `consumption_receipt {path, sha256, consumed_at_monotonic_ns}`
- `t0_to_arm_ns`, `arm_to_consume_samples_ns`, `arm_to_consume_p99_ns`
- pack SHA, reviewed-main SHA, and boot UUID shared by all three events.

The arm receipt currently has UTC issuance and expiry but no arm monotonic timestamp (`joulewise/arm_readiness.py:6243-6262`); that needs a schema amendment. Consumption already records a monotonic timestamp and refuses post-expiry use (`joulewise/arm_readiness.py:7910-7914`).

Magistrate ruling needed: define the p99 estimator for the one-event shakedown. Recommended conservative definition: nearest-rank p99 of every shakedown arm→consume event; with the D-078 no-retry single arm, p99 equals that one observed value. Do not interpolate or borrow historic measurements.

### F3 — B-22 boundary

B-22 blocks claim-window close-out, not the diagnostic shakedown; its cure must land before the first claim close-out, and shakedown records under the uncured validator cannot be promoted (`custody-staging/rulings-r5-consolidation.md:21-30`).

Current `validate_window_duration_margins_receipt()` validates only self-consistency of a supplied receipt (`joulewise/window_duration_margins.py:1032-1173`). At `5bd7acf`, only the margins module and recorder reference it; there is no consumer. The cure must therefore provide a distinct pack-aware claim-close-out validator that compares the receipt’s cell inventory, member pins, pack-tree hash, registry source hash, and evaluation-basis binding against the selected frozen pack—not merely against its own repaired SHA.

The scheduler’s B-22 pre-admission check is only a prevention of an uncloseable claim window. It does not substitute for the post-window consumer, and it must not evaluate or block a shakedown close-out.

### What this layer does not do

- It does not alter either 300 s policy value, the 15-minute or four-minute limits, or invent another margin. Those are r3/V5 values.
- It does not treat a capture’s projected multi-hour span as the fuse projection.
- It does not waive C1–C5, auto-retry a refusal, or authorize hands-required work.
- It does not block the non-claim shakedown for missing B-22 cure, nor promote that shakedown afterward.
- It does not fold the separate family-publication-marker schema/consumer into this change. r5 V-6 requires that design and the scheduler-gate design to each receive their own D-144 round before implementation (`custody-staging/rulings-r5-consolidation.md:159-164`; `docs/decision_log.md:167`).

### Staged implementation write scope

1. B-22 cure, first:

   `joulewise/window_duration_margins.py`, `scripts/record_window_duration_margins.py`, `tests/test_window_duration_margins.py`

2. Receipt/timing contract:

   `joulewise/arm_readiness.py`, `scripts/generate_arm_readiness.py`, `tests/test_arm_readiness.py`, `tests/test_arm_readiness_lifecycle.py`, `docs/process/d149-go-receipt-template.md`

3. Scheduler and enforced launch seam:

   `joulewise/window_scheduler_gates.py`, `scripts/evaluate_window_scheduler_gates.py`, `scripts/launch_window.py`, `tests/test_window_scheduler_gates.py`, `tests/test_launch_window.py`

4. Lead-owned ruling/custody updates remain outside an implementation worker’s scope: `docs/decision_log.md`, `RUN_STATE.md`, `TASK_QUEUE.md`, and process-trace rulings.

## Residual risk

Focused tests were not runnable because the read-only sandbox has no writable temporary directory. The next implementation pass should run the listed focused tests plus the canonical suite in a writable worktree.