```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "partial",
  "summary": "The already-merged inactive quiet guard now distinguishes proven process-identifier reuse from same-start observation churn, with focused counterfactual tests; live installation, independent review, and kernel reconciliation remain lead-owned.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-fan-QUIET-GUARD-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/QUIET-GUARD-01/01-sol-report.md",
    "joulewise/quiet_guard_process.py",
    "scripts/setup_quiet_guard.sh",
    "tests/test_quiet_guard.py",
    "tests/test_quiet_guard_process.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_quiet_guard_process tests.test_quiet_guard",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 106 tests in 2.503s",
          "",
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 106 tests in .*s\\n\\nOK \\(skipped=1\\)"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "/bin/sh -n scripts/setup_quiet_guard.sh",
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
      "id": "V3",
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
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The explicit live-Darwin inventory test was skipped by the focused module run, and the root-owned helper was not installed or exercised.",
      "needs": "The lead must run the live Darwin test; Ed or the lead must perform the interactive inactive installation and inspect its status before claiming installed-host acceptance."
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "blocking",
      "text": "The kernel row remains queued and still names the pending T3-CHAR-PAIR-01 dependency and superseded full-rollout acceptance, although D-114 shelved that dependency and PR #107 merged commit 1.",
      "needs": "The magistrate must reconcile docs/process/state_kernel.json and its generated projections without reviving commits 2-4."
    },
    {
      "id": "F3",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING QG-R1: no cited ruling says whether installed-INACTIVE acceptance means reviewed installable bytes or an installation observed on Ed's host.",
      "needs": "Choose (A, recommended) keep acceptance pending until the inactive install and status check run on Ed's host, or (B) close the software row after review and register host installation as a separate live task. Only row closure is blocked; the desk implementation is complete."
    },
    {
      "id": "F4",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "This fix has focused tests but has not received the independent audit and delta re-audit required by the row's gauntlet acceptance.",
      "needs": "After harvest, run an independent contract audit over the final committed diff, fix any finding, and re-audit every fix round."
    }
  ]
}
```

## Change

Commit 1 was not absent: repository history shows merge commit `e6db69aa4547341fd3a667cd98e1c9ff66681bc5` (PR #107), and the source already provides the host-wide durable lease, single-snapshot process census, fixed privileged helper, refusal-only arm command, and inactive configuration described by D-114, D-115, and `docs/contracts/quiet_guard.md`.

The desk audit found one residual contract defect. `revalidate_identity()` classified every complete-identity disagreement as process identifier reuse. The contract reserves that classification for a different kernel start-time anchor. The implementation now returns `PID_REUSED` only when the accepted process-table start time changed; a same-start executable, argument-vector, or ancestry disagreement returns `UNOBSERVABLE`. `audit_registry()` therefore records canonical cause `process_observation_unavailable` and retains custody instead of asserting reuse without its required evidence. The installer's reviewed-artifact digest was refreshed to authenticate the changed module.

The new tests are counterfactual-shaped: deleting the start-time discriminator makes the primitive test and the registry-audit integration test fail.

### Scoped design

**Forcing problem.** A process identifier can be reused only after the earlier process exits. The accepted kernel start time is the evidence that separates reuse from an observation race. Calling a same-start identity change “reuse” makes the durable event claim more than the snapshot proves.

**Options.** (A) Treat any complete-identity change as reuse; rejected because it contradicts the contract. (B) Use the accepted start-time anchor as the discriminator; adopted because it uses the already-frozen snapshot and changes no schema. (C) acquire another process-table snapshot; rejected because the adopted census design makes a fresh command invocation, not an internal resnapshot, the retry boundary.

**Worked example.** If the expected and observed rows have the same process identifier and start time but different arguments, observation is unavailable and custody stays retained. If the process identifier matches but the observed start time is a later start time, reuse is proven and may be recorded as such.

### Finding and decision table

| Finding | Evidence | Decision | State |
|---|---|---|---|
| Same-start identity churn was labeled as process-identifier reuse | `joulewise/quiet_guard_process.py`; the exact-identity section of `docs/contracts/quiet_guard.md` | Compare the accepted row's start time before returning `PID_REUSED` | Implemented and focused-test green |
| Commit-1 machinery already existed at intake | Merge `e6db69aa4547341fd3a667cd98e1c9ff66681bc5`; D-114; PR #107 subject | Preserve the landed design and make only the contract repair | Implemented |
| Kernel row conflicts with its own D-114 status note | `docs/process/state_kernel.json` row `QUIET-GUARD-01`; D-114 | Do not edit magistrate-owned state; request reconciliation | Pending magistrate action |
| Host installation meaning is not settled by the cited rulings | D-114 says installed inactive; D-115 governs installer authority | NEEDS_RULING QG-R1, recommendation A | Blocking row closure only |

## Verification notes

The repository-wide test suite was not run, as the mission preflight expressly prohibited it. The focused run skipped only `LiveDarwinKernelInventoryTests`, whose class requires Darwin plus explicit `QG_LIVE_DARWIN=1` opt-in. No production state root, privileged helper, launch agent, quiet-window capture, or user custody path was touched.

## Residual risk

Exact next steps:

1. The magistrate harvests this diff, commits it, and runs the row-required independent contract audit plus delta re-audit.
2. The lead runs `QG_LIVE_DARWIN=1 python3 -m unittest tests.test_quiet_guard_process.LiveDarwinKernelInventoryTests` on the target Mac.
3. Subject to QG-R1, Ed or the lead runs `scripts/setup_quiet_guard.sh` interactively, then checks `/usr/bin/sudo -n /usr/local/libexec/joulewise-quiet-guard status` for inactive configuration, idle state, empty registry and custody roots, and a null lease. This session did not exercise root authority.
4. The magistrate updates the prohibited kernel and generated queue/state projections to apply D-114, remove the moot `T3-CHAR-PAIR-01` dependency, cite PR #107 plus this repair, and close only the commit-1 scope. Commits 2-4 remain shelved.
