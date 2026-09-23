```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "One blocker: broken capture-path symlinks permit early release; the new driver probe also has narrower coverage than the updated docs claim.",
  "workspace": {
    "base_requested": "4c76ab69..3e27057a",
    "base_mode": "exact",
    "head_start": "14c0e06bb690fac79c9b2d62c1db220f6b905c2c",
    "head_end": "14c0e06bb690fac79c9b2d62c1db220f6b905c2c",
    "upstream_end": "14c0e06bb690fac79c9b2d62c1db220f6b905c2c",
    "branch": "feat/2026-09-23-refusal-early-release-f3"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "file_line": "scripts/magistrate_watchdog.py:801,829,834",
        "counterexample": "A broken symlink at night/evidence, night/evidence_envelopes.jsonl, or RUNS_ROOT/instrument_validation is treated as absence; a delivered bare-C5 refusal reaches LAUNCHING and latches.",
        "executed_evidence": "Synthetic decide() probes returned LAUNCHING with latch 1 for all three broken-symlink cases. A regular evidence file and an index directory returned FENCED."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "file_line": "scripts/magistrate_watchdog.py:1607; docs/process/NIGHT_HANDBACK.md:57; docs/phase_2/derivation_night_runbook.md:1856",
        "counterexample": "With courier.sent present after completion and a live run_night.py dead-man row, decide() returns LAUNCHING without calling driver_probe. It likewise does not probe again after an early-release latch.",
        "executed_evidence": "The focused harness returned driver_deadman_after_completion LAUNCHING, driver_calls 0, and driver_live_after_latch LAUNCHING, additional_driver_calls 0. Pending release with driver_probe=None or probe exit 2 or 3 held correctly."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_magistrate_watchdog.py tests/test_arm_retry.py tests/test_evidence_night.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["268 passed, 351 subtests passed in 698.62s (0:11:38)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "268 passed, 351 subtests passed"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/f2d6899b-scratch-delta/probe.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "driver-error3 decision HOLD_CENSUS"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/f2d6899b-scratch-delta/latch_probe.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["driver_deadman_after_completion LAUNCHING driver_calls 0"]
      },
      "expected": {"exit_code": 0, "tail_regex": "driver_deadman_after_completion LAUNCHING driver_calls 0"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/f2d6899b-scratch-delta/enumerate.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["(True, True, True, 'REFUSED', 'before_completion', False, True)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "cases 72 differences 3"}
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/f2d6899b-scratch-delta/count_paths.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["two_installed_plists LAUNCHING delivered_evaluations 5"]
      },
      "expected": {"exit_code": 0, "tail_regex": "delivered_evaluations 5"}
    }
  ],
  "flags": []
}
```

## Findings

**F1 — BLOCKER.** [`_tree_has_match`](/Users/edr/code/wt-f2d6899b-f3/scripts/magistrate_watchdog.py:801) treats `FileNotFoundError` at its root as an absent directory. A broken symlink is therefore accepted as positive evidence of no capture. Through `decide()`, broken links at either evidence path and at the calibration capture directory all produced `LAUNCHING` and a release latch. Permission denial and a symlink loop at the evidence root held closed in separate probes. Distinguish a genuinely absent path from an existing broken link before granting release.

**F2 — SHOULD-FIX.** The driver probe runs only for a pending early-release candidate ([code](/Users/edr/code/wt-f2d6899b-f3/scripts/magistrate_watchdog.py:1607)). Both updated paragraphs say it runs on each tick in the stated interval ([handback](/Users/edr/code/wt-f2d6899b-f3/docs/process/NIGHT_HANDBACK.md:57), [runbook](/Users/edr/code/wt-f2d6899b-f3/docs/phase_2/derivation_night_runbook.md:1856)). An executed after-completion case with `courier.sent` and a live `run_night.py dead-man` returned `LAUNCHING` with zero driver-probe calls. After a latch, a newly live driver also leaves `LAUNCHING`; that part follows the explicit one-way latch design. The after-completion fallthrough existed in the base, but the new probe does not provide a global “any live driver holds” check. Clarify the intended boundary and make the prose describe the implemented one. The mandated first-use glosses for machine state, tick, notice, and owner veto are present.

The 20,000-file custody tree took **52 ms** for one `decide()` call: three `_delivered_zero_capture_refusal` evaluations and six `_tree_has_match` calls, with 49 ms in walks. With both night plists installed, the refusal check ran **five** times per decision; `retained_roots` adds one `plan_span_active` evaluation outside that decision. Driver-probe absence, exit codes 2 and 3, and a live driver on a pending release all held correctly.

The SHA latch lookup from `evidence_night` found its sibling watchdog state, and removing the plan pruned its key. Across 72 file-presence/time combinations against `af879efb`, there were three pre-completion differences: two intended unlatch-held zero-capture refusals and one started, exited, delivered REFUSED chain kept armed through completion. With the latch present, only that last difference remained. No undelivered dead-man-tail regression appeared.

## Residual risk

Live `pgrep`, launchd, and real custody state were **NOT EXECUTED**. The 20,000-file timing is a synthetic warm-cache measurement; permission denial was simulated. The requested three test modules passed, and the repository worktree remained clean.