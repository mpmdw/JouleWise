```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "F1 survives as a narrowed blocker, F3 is confirmed, and F2 reduces to stale-state reconciliation rather than three missing launch blockers.",
  "workspace": {
    "base_requested": "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
    "base_mode": "exact",
    "head_start": "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
    "head_end": "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
    "upstream_end": "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
    "branch": "worktree-agent-a1abb9d2a4a1e0aa7"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "verdict": "PARTIAL",
        "survives": "The authoritative kernel has zero global gates and renders P2-006 READY despite the explicit no-window-before-council ruling; the D-117 collection program has no live selection row.",
        "refuted": "D-117 does not expressly retire P2-006; it replaces the paper claim path and orders its closure before broader campaigns.",
        "remedy": "Install the council global gate immediately, represent or explicitly admit the D-117 window work, and obtain a separate disposition of P2-006."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "verdict": "CONFIRMED",
        "survives": "Arm receipt consumption exists, but the launch command neither consumes nor validates its output and downstream claim consumers do not authenticate launch-consumption lineage.",
        "refuted": "The arm receipt itself is not orphaned: generate_arm_readiness.py consume is a real machine consumer.",
        "remedy": "Contract-first launch wrapper that consumes then execs the frozen chain, plus downstream refusal when matching launch-consumption provenance is absent."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "verdict": "PARTIAL",
        "survives": "Live-state bookkeeping is stale: completed work remains as apparent hand-written work orders, and completed U11/FCM work remains queued or described as unmerged in the kernel.",
        "refuted": "The three prose work orders are not current missed launch blockers: all three implementations are ancestors of HEAD. D-133 also continued FCM as desk work rather than disposing it.",
        "remedy": "Archive/relabel the stale prose and remove completed U11/FCM rows from the live kernel; do not re-add the three completed work orders as blockers."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --quiet ac3fe1d2fb46ab02b2f70eba387165d63bc1de6b..HEAD -- TASK_QUEUE.md docs/process/state_kernel.json docs/phase_2/window_runbook.md docs/decision_log.md; printf 'targeted_diff_exit=%s\\n' \"$?\"; shasum -a 256 docs/process/state_kernel.json docs/phase_2/window_runbook.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "targeted_diff_exit=0",
          "f85ea9647353d177929df47c77d515c8379a24e2ed86d9ab0ca266c89b29643b  docs/process/state_kernel.json",
          "25a4e809461f681d39d4decb7ca43eac1ec2fd61abe12ffc58d7167b3c68e3da  docs/phase_2/window_runbook.md"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "targeted_diff_exit=0"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "jq -r '.active_global_gates | length, .[]?.id' docs/process/state_kernel.json",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["0"]},
      "expected": {"exit_code": 0, "tail_regex": "^0$"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "jq -r '.tasks as $t | [\"WO-MINT-ESTIMATOR-VOCAB\",\"WO-COLLECTION-MARGIN-01\",\"WO-ARM-EVIDENCE-AUTHOR-01\"][] as $id | [$id,($t|has($id))] | @tsv' docs/process/state_kernel.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "WO-MINT-ESTIMATOR-VOCAB\tfalse",
          "WO-COLLECTION-MARGIN-01\tfalse",
          "WO-ARM-EVIDENCE-AUTHOR-01\tfalse"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "WO-ARM-EVIDENCE-AUTHOR-01\\s+false"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "rg -n 'arm[_-]?receipt|arm_readiness|launch_consumption|consumption_sha256' scripts/run_campaign.py scripts/backup_runs.sh scripts/extract_detection_floors.py scripts/mint_floor_artifact.py scripts/mint_floor_artifact_generalized.py scripts/record_window_duration_margins.py joulewise/whole_window.py joulewise/floor_extraction.py joulewise/detection_floor.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 1, "tail": []},
      "expected": {"exit_code": 1, "tail_regex": "^$"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git status --short --branch; git rev-parse HEAD; git rev-parse '@{upstream}'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## main...origin/main",
          "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
          "8937dec9bd7be8f6d87694a739089ac8434b8bc9"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "8937dec9bd7be8f6d87694a739089ac8434b8bc9"}
    }
  ],
  "flags": [
    {
      "id": "ENV1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The delegated worktree disappeared after initial verification; review continued read-only from clean main at the identical requested HEAD without checkout or branch switching.",
      "needs": ""
    },
    {
      "id": "BASE1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The manifest pins ac3fe1d; requested HEAD 8937dec adds README.md, RUN_STATE.md, and the manifest. Targeted kernel/runbook/queue/decision files are unchanged, pinned hashes match, and current RUN_STATE was independently re-read.",
      "needs": ""
    }
  ]
}
```

## Findings

### F1 — PARTIAL, blocker

The core gate defect is confirmed. D-063 makes the kernel authoritative for work selection and adds conjunctive global gates (`docs/decision_log.md:3330-3354`); DOC-008 requires the kernel to be the only editable source of live ordering/status and defines global-gate selection semantics (`docs/specs/c027/doc-008_state_kernel.md:7-17,185-212`). Ed’s later ruling says no window runs before a comprehensive council verdict (`docs/decision_log.md:8847-8861`), while the charter defines council READY and separates it from later T-0 GO (`docs/process/instrument-readiness-audit-charter.md:79-90`).

Independent probes found:

- `jq -r '.active_global_gates | length, .[]?.id' …` returned `0`.
- `RUN_STATE.md:3419-3433` consequently renders no gate and `READY — Q2 P2-006`.
- `python3 scripts/gen_state.py --check` exited 0 with no output, proving the generator accepts this policy contradiction.
- Searching kernel task IDs/goals for D-117, ALPHA, BETA, GAMMA, and three-window terms found only `D117-U11-IDPIN-PROJECTION`; no ALPHA/BETA/GAMMA collection-selection row exists.

The refuted portion is that D-117 itself formally supersedes `P2-006`. D-117 expressly supersedes D-110’s historical re-mint, adopts three prospective claim windows, and orders that P1 closure before broader campaigns (`docs/decision_log.md:7650-7678`); it never names or retires `P2-006`. Therefore deleting `P2-006` without a ruling would overreach. Blocker severity remains correct because the explicit all-window council gate is absent from the authoritative selector.

Remedy shape is sound only if narrowed: add an active global gate covering quiet-window selection with council READY as clearance; represent the D-117 windows as kernel tasks or expressly admitted non-kernel work; separately rule whether `P2-006` remains later research work.

### F3 — CONFIRMED, blocker

The required ceremony exists. D-134 requires an atomically consumable single-launch capability and places atomic consumption at the end of the critical path (`docs/decision_log.md:8620-8636`). The runbook requires ARM, verify, then consume, and says physical launch follows successful consumption (`docs/phase_2/window_runbook.md:802-884`).

The implementation does machine-consume the arm receipt: `scripts/generate_arm_readiness.py:51-55,108-115` calls `consume_launch_capability`. But that function explicitly “never execute[s] a command” (`joulewise/arm_readiness.py:4025-4032`) and merely emits a consumption receipt (`joulewise/arm_readiness.py:4085-4095`). The actual launch remains an independent `caffeinate … window-chain.zsh` command (`docs/phase_2/window_runbook.md:1144-1148`).

Independent absence searches found:

- The runbook chain body at lines 964–1148 contains no arm-receipt, readiness, consumption, or capability check.
- Exact production searches for `"launch_consumption"`, its schema, validator, and `consumption_sha256` found ownership only in `joulewise/arm_readiness.py`.
- A separate inventory/search across campaign execution, backup, extraction, margin, floor, whole-window, and both mint paths exited 1 with no matches.
- `arm_readiness_evidence_t0.py:1501-1532` checks only that arm/consumption namespaces are empty before authoring the capability; it is not a launch or downstream consumer.
- The sole later requirement is the human close-out record entry at `docs/phase_2/window_runbook.md:1509-1518`.

Thus a direct invocation can bypass ARM/consume without machine refusal, and later claim machinery has no authenticated launch-consumption lineage to reject. Blocker severity is correct. The repair should preserve the contract’s rule that Ed—not an automated verdict—performs the physical launch: define a reviewed launcher that atomically consumes and immediately `exec`s the frozen chain, then require downstream verdict/mint provenance to authenticate that exact consumption receipt. The contract/runbook should specify this binding and crash semantics before implementation.

### F2 — PARTIAL, should_fix

The structural stale-state defect is confirmed, but the claimed live blocker set is not.

The sole generated queue is `TASK_QUEUE.md:452-613`, while the three named sections sit outside it at lines 201, 635, and 659. All three are absent from the kernel. However ancestry probes returned exit 0 for every implementation:

- `e11b1ad` — WO-MINT-ESTIMATOR-VOCAB.
- `1092984` — WO-COLLECTION-MARGIN-01.
- `ac3fe1d` — WO-ARM-EVIDENCE-AUTHOR-01.

Therefore these are obsolete registration narratives, not current launch-blocking work the kernel failed to schedule.

The kernel nevertheless contains real falsehoods:

- `D117-U11-IDPIN-PROJECTION` remains queued and says packs are unprojected (`docs/process/state_kernel.json:845-884`), while all three checked-in projection receipts and freeze receipts report `PASS`; U11 and the later freeze work are ancestors of HEAD.
- `FLOOR-COMMONMODE-01` says work “continues unmerged” (`docs/process/state_kernel.json:1160-1189`), but FCM commit `60d9e42` is an ancestor of HEAD.
- D-133 did not dispose FCM: it expressly continued it as an unmerged desk thread (`docs/decision_log.md:8463-8484`). The row became false because the thread subsequently merged, not because D-133 required shelving.

Under DOC-008, authority is not legitimately bifurcated—the kernel wins—but stale prose and terminal rows make the declared authority unreliable to humans while `gen_state --check` remains green. This is `should_fix`, not an independent blocker: archive or relabel the completed prose, remove completed U11/FCM from the live kernel, regenerate, and add a reconciliation check for completed implementation ancestry/receipts. Re-registering the three completed work orders as live blockers would be the wrong repair.

### Synthesis

F1 survives as a blocker, although its assertion that D-117 formally killed `P2-006` dies; F3 survives as a blocker, with the correction that the arm receipt does have a consumer—the orphan is the consumption-to-launch/downstream lineage; F2 survives only as a should-fix stale-authority defect, while its three-missed-live-blockers premise dies. No whole finding is fully refuted. The minimal true work-order set is two items: one kernel reconciliation order installing the council gate, disposing completed rows/prose, and ruling `P2-006`/D-117 representation; and one contract-first launch-lineage order coupling atomic consumption to the frozen launch and requiring downstream authenticated provenance.

## Residual risk

The off-repository final arm packet and instantiated `$WINDOW_PLAN_ROOT/window-chain.zsh` were outside the workspace sandbox, so they were not inspected. The pinned repository runbook hash matched the audit manifest, its full chain template was inspected, and no quiet-window or hardware execution was attempted.