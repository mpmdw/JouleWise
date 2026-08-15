```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "F1 and F3 are confirmed blockers; F2's authority-drift core survives, but its three-open-work-orders scenario is stale and overstated.",
  "workspace": {
    "base_requested": "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
    "base_mode": "exact",
    "head_start": "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
    "head_end": "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
    "upstream_end": null,
    "branch": "worktree-agent-ac7155f6658f72a6d"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "verdict": "CONFIRMED",
        "title": "Quiet-window work selection fails open despite the binding council gate and D-117 supersession",
        "severity_judgment": "correct",
        "remedy": "Encode the council gate in active_global_gates, retire/supersede P2-006, and represent the actual D-117 window program in the kernel."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "verdict": "PARTIAL",
        "title": "Kernel/prose bifurcation and material kernel falsehoods survive; the alleged three currently-open universal launch blockers do not",
        "severity_judgment": "correct for the authority defect, overstated for the individual work-order scenario",
        "remedy": "Reconcile completed and genuinely live work into one kernel transaction; do not blindly add the three already-shipped work orders as active rows."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "verdict": "CONFIRMED",
        "title": "Arm capability consumption is mechanically sound but disconnected from the executable launch entrypoint",
        "severity_judgment": "correct",
        "remedy": "Ship one fail-closed launcher that consumes/revalidates the capability and immediately execs the chain; make direct chain invocation without that binding refuse before settle."
      }
    ],
    "minimal_work_orders": [
      "One state-kernel reconciliation covering F1 and the surviving F2 drift",
      "One atomic arm-consume-to-launch binding covering F3"
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
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
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_gen_state.TestWorkSelectionFidelity.test_frozen_historical_gate_artifact_suppresses_exactly tests.test_gen_state.TestWorkSelectionFidelity.test_gate_rendered_in_both_regions_and_forbidden_tasks_never_ready tests.test_gen_state.TestWorkSelectionFidelity.test_live_kernel_renders_ungated_and_a_gate_renders_gated",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 3 tests in 0.029s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 3 tests.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "for each D-117 pack: run shasum -a 256 -c from identity_pin_projection.receipts and arm_readiness.freeze.receipts",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "projection-0001.json: OK",
          "freeze-0001.json: OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "projection-0001.json: OK.*freeze-0001.json: OK"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "sed -n '965,1141p' docs/phase_2/window_runbook.md | /bin/zsh -n; echo chain_syntax_exit=$?; sed -n '965,1141p' docs/phase_2/window_runbook.md | rg -n -i 'ARM_RECEIPT|PACK_ROOT|arm_readiness|consum|verify' || true",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "chain_syntax_exit=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "chain_syntax_exit=0"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_arm_readiness_integration tests.test_arm_readiness_lifecycle",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 21 tests in 1.716s",
          "FAILED (errors=18)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 21 tests.*OK"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD && git status --short --branch && git diff --name-only && git diff --cached --name-only",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
          "## main...origin/main"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "8937dec9bd7be8f6d87694a739089ac8434b8bc9.*main\\.\\.\\.origin/main"
      }
    }
  ],
  "flags": [
    {
      "id": "ENV1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The delegated worktree was concurrently removed after a clean exact-HEAD preflight. Review continued from clean main at the identical commit; no repository delta or attribution ambiguity resulted.",
      "needs": ""
    },
    {
      "id": "VG1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The read-only sandbox exposed no writable temporary directory. Receipt-generation tests failed at tempfile.TemporaryDirectory before executing 18 filesystem scenarios; three non-writing tests passed. Static launch-path evidence remains decisive.",
      "needs": "Optionally rerun V5 in a writable disposable TMPDIR; do not run a quiet-machine campaign as part of that replay."
    }
  ]
}
```

## Findings

### F1 — CONFIRMED (blocker)

Independent probes reproduced the finding.

- `jq` showed `active_global_gates: []`; `docs/process/state_kernel.json:2` confirms it.
- `python3 scripts/gen_state.py --check` exited 0 even though the generated restart view says no global gate and selects `P2-006` as READY: `RUN_STATE.md:3419-3433`.
- The binding directive says a comprehensive council verdict precedes any window: `docs/decision_log.md:8847-8861`.
- D-117 supersedes the historical program with alpha, beta, and gamma: `docs/decision_log.md:7635-7677`. Nevertheless, the selected kernel row remains the old “Window A two-model campaign”: `docs/process/state_kernel.json:1755-1857`.
- Two independent kernel inventories—task-key matching for `D117|ALPHA|BETA|GAMMA|READINESS|COUNCIL` and content matching for `prospective.*claim.*window|window.*audit`—found only `D117-U11-IDPIN-PROJECTION`, not the three-window program or readiness council.
- The gate mechanism is operational, not hypothetical: `scripts/gen_state.py:457-475` excludes lane tasks, and `:496-518` renders active gates. Three focused gate tests passed and proved a synthetic audit gate removes all READY rows.

Severity is correctly blocker: the authoritative selector licenses an obsolete quiet-machine campaign across an explicit apex gate. Remedy shape is sound, but should be one atomic kernel repair: install a quiet-Mac council gate, remove/supersede `P2-006`, and enroll the real D-117 program.

### F2 — PARTIAL (blocker authority defect; scenario narrowed)

The authority bifurcation and one material falsehood are confirmed:

- The generated queue is fenced at `TASK_QUEUE.md:452-613`, while the three work-order sections sit outside it at `TASK_QUEUE.md:201`, `:635`, and `:659`.
- Literal-ID, normalized-slug, schema-key, and script-inventory searches found none of those three IDs in the kernel. `gen_state --check` still exits 0 because it compares only marker replacement output (`scripts/gen_state.py:800-809`).
- The U11 row is unambiguously false: it says `queued` and “packs remain unprojected” at `docs/process/state_kernel.json:845-884`. All three projection receipts instead report `PASS` and name that work order, e.g. the alpha receipt at `configs/campaigns/d117_floor_qwen25_1p5b_v1/identity_pin_projection.receipts/projection-0001.json:684-689`; all projection and freeze sidecars verified.
- `FLOOR-COMMONMODE-01` is still queued and says work “continues unmerged” at `docs/process/state_kernel.json:1160-1189`, despite main containing the relevant FCM and mint-vocabulary commits.

What does not survive unchanged:

- Only `WO-ARM-EVIDENCE-AUTHOR-01` is labeled universally launch-blocking (`TASK_QUEUE.md:659`). `WO-MINT-ESTIMATOR-VOCAB` is explicitly conditional at `:203-215`; collection-margin governs the freeze mechanism and postcollection close-out rather than every launch.
- All three implementations are already on this HEAD: `e11b1ad` (mint vocabulary), `1092984` (collection margins), and `ac3fe1d` (arm evidence/chain repairs). The shipped inventory includes `joulewise/floor_mint_estimator.py`, `scripts/record_window_duration_margins.py`, and `scripts/author_arm_evidence_t0.py`.
- D-133 calls FCM a continuing non-freeze-gating desk thread; that alone does not prove “disposed work.”

Thus the blocker is the false authoritative state, not three currently missing implementations. The remedy should reconcile closures and genuinely live work in the kernel, not add all three stale prose sections as active rows.

### F3 — CONFIRMED (blocker)

The earlier producer gap is closed, but the launch-enforcement gap remains.

- Shipped tooling now exposes `arm`, `verify`, and `consume`, plus the fifteen-receipt author: both `python3 scripts/generate_arm_readiness.py --help` and `python3 scripts/author_arm_evidence_t0.py --help` succeeded.
- `consume_launch_capability` fully verifies and atomically writes a consumption receipt, but explicitly “never execute[s] a command”: `joulewise/arm_readiness.py:4025-4033`. The CLI merely invokes that function at `scripts/generate_arm_readiness.py:103-115`.
- The runbook then launches separately. The chain accepts only `$1`, the plan root (`docs/phase_2/window_runbook.md:964-971`), and directly calibrates/collects at `:1101-1141`. The launch recipe passes only that same plan root at `:1144-1148`.
- Extracting the chain and running `/bin/zsh -n` exited 0. Searching the exact executable block found no `ARM_RECEIPT`, `PACK_ROOT`, arm-readiness verifier, or consumption reference.
- The three-night packet repeats the separation for all three packs: consume manually, then invoke raw `window-chain.zsh`; see `docs/strategy/2026-08-07-three-night-operator-packet.md:139-161`, `:290-311`, and `:419-440`.
- Independent production-code inventory found arm generation/verification/consumption only in `joulewise/arm_readiness.py` and `scripts/generate_arm_readiness.py`; the consumption namespace is additionally inspected by `joulewise/arm_readiness_evidence_t0.py`. Neither `scripts/run_campaign.py` nor the chain imports or validates arm readiness.
- The T-0 author verifies that an exact launch command exists and that arm/consumption namespaces are initially empty (`joulewise/arm_readiness_evidence_t0.py:1501-1533`); it cannot bind the later consumption to execution.

The severity is correctly blocker: a skipped manual step can spend the entire quiet window normally. The minimal remedy is an executable launch admission boundary—not another checklist or close-out check. A single launcher should consume/revalidate the capability and immediately `exec` the chain, while direct chain invocation without the bound consumption context refuses before the first settle.

### Synthesis

F1 survives fully; F2 survives only as a state-authority blocker, while its claim that three universal implementation obligations remain open dies; F3 survives fully despite the now-shipped evidence producer. The minimal true program is therefore two work orders: one atomic state-kernel reconciliation combining the council gate, D-117 campaign enrollment, obsolete `P2-006` retirement, and stale-row/work-order closure; and one atomic launch-admission repair binding arm capability consumption to the only executable window entrypoint. No separate producer, collection-margin, or mint-vocabulary implementation work order is justified at this HEAD.

## Residual risk

The sandbox prevented a fresh GO-receipt generation/consumption replay because every writable temporary-directory probe was denied before fixture setup; no repository path was touched. No live launch was attempted because that would violate the bridge’s `[QUIET-MAC]` prohibition. Final HEAD remained `8937dec…`, main was clean, and the baseline hashes for the state kernel, runbook, and row registry matched the manifest.