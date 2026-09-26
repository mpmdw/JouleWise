```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "FIX-FIRST: the required pin proof is nonempty, the AST guard misses a specified case, the obligations source remains stale, and two required regression tests fail in this environment.",
  "workspace": {
    "base_requested": "3e984ecc",
    "base_mode": "descendant",
    "head_start": "3ad48d1e52451914aeca30f583bea1f5bdd31b34",
    "head_end": "3ad48d1e52451914aeca30f583bea1f5bdd31b34",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "FIX-FIRST",
    "findings": [
      {
        "id": "R1",
        "severity": "blocker",
        "text": "The charged c6814dd8..a44f0685 pin proof is nonempty: the preregistration file under configs changed by 22 lines after the main merge. The lead must rule on a corrected baseline or proof scope."
      },
      {
        "id": "R2",
        "severity": "should_fix",
        "text": "The AST guard applies its guarded-string rule only when source contains the literal battery_float, contrary to §3.10. A scratch dynamic-import consumer using the string validate_window produced zero violations."
      },
      {
        "id": "R3",
        "severity": "should_fix",
        "text": "The obligations v1.1 §4.5 source still directs consumers to call verdict primitives and describes the retired continuation path. The round-7 report labels its replacement text as for the lead to land."
      },
      {
        "id": "R4",
        "severity": "should_fix",
        "text": "Two required importer modules are not green here: the live OS probe gets None because sysctl is denied, and the unchanged bind-supervision watchdog times out. Both failures reproduced in isolated reruns."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_battery_float_consumers",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 9 tests in 9.972s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_issue_calibration_acceptance_generation",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 156 tests in 172.267s", "FAILED (failures=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_exits",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 48 tests in 502.010s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 237 tests in 148.196s", "FAILED (failures=1, skipped=9)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_round7_artifacts",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 69 tests in 521.880s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --stat c6814dd8 a44f0685 -- joulewise/calibration_bracketing.py joulewise/adapters/powermetrics.py joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/reduce.py protocol_v3.json scripts/night_chains configs scripts/paper_anchor_correction_quantified.py",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 0, "tail": [".../preregistration_d079_epoch_25g83_rev1.md | 22 ++++++++++++++++++++--", "1 file changed, 20 insertions(+), 2 deletions(-)"]},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "R1 comes from main commits that sealed Revision 5 and appended A-R5b; making the specified proof empty would conflict with those changes.",
      "needs": "Rule a corrected pin baseline or path scope before merge."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "/usr/sbin/sysctl -n kern.osversion returns Operation not permitted in this sandbox; the bind-supervision timeout also reproduces in isolation.",
      "needs": "Rerun the two named tests in the lead's supported environment."
    }
  ]
}
```

## Findings

- **R1 — BLOCKER.** The exact pin command returns one changed file, [the Revision 5 preregistration](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-sol/configs/calibration/preregistration_d079_epoch_25g83_rev1.md). Its seal and A-R5b amendment came from main commits `23dd9909` and `ad7565a7`. The paper tool itself **is** byte-identical to `c6814dd8`: both SHA-256 values are `3844a8f1eefb8b898a30b96f524e0af0da3af98fc2e6d0ecb78ea1d1f8d303f1`. The lead needs to rule on the pin proof’s baseline or path scope.

- **R2 — MATERIAL.** [The guard](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-sol/tests/test_battery_float_consumers.py:64) narrows §3.10’s string rule to files containing the literal `battery_float`. In `/tmp` copies, a new direct `validate_window` call was flagged at cadence line 83. A consumer using `importlib.import_module("joulewise.battery_" + "float")` and `getattr(module, "validate_window")` returned **zero** violations. The other two scratch mutations were killed by parity assertions: a caught-and-continued refusal and a named-only collector each caused two assertion failures; their unmutated controls caused zero.

- **R3 — MATERIAL.** [Obligations §4.5](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-sol/docs/process_traces/2026-09-25-activation-ed17a643/bfg-d/06-harvest-final-obligations-v1.1-source.md:170) still names direct `validate_window` and `load_committed_verdict` calls and the retired continuation consumer. That file has no change in the audited range. The replacement in [the round-7 seat report](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-sol/docs/process_traces/2026-09-25-activation-ed17a643/bfg-d/25-seat-report-r7.md) is explicitly marked “for the lead to land.”

- **R4 — MATERIAL verification gap.** The importer sweep had two reproducible failures in unchanged paths. `test_live_probes_report_this_machine_against_the_active_epoch` received `os_build=None`; `/usr/sbin/sysctl -n kern.osversion` returns `Operation not permitted` here. `test_blocked_journal_never_blocks_deadline_or_grants_go` exceeded its 8 second subprocess watchdog on both runs. Neither failure establishes a battery-verdict regression, but the required sweep is not green.

The charged behavior otherwise held in executed tests: P3, P4, P5, the F1 forged-record reproduction, target-epoch parity, ledger refusal, and the H-2 byte-identity assertion passed within the issuer and calibration suites. `check` and `prepare-candidate` call the same collector with their registration IDs, repository root, derived `target_epoch`, and digest. Both use `battery_epoch_policy`; the production re-grep found no other verdict consumer outside the seam and the allowlisted harvest writer. The fixture flag returned argparse exit 2 with “battery probe fixture requires the logical sampler test mode” both without test mode and with `--sampler-direct-for-test` alone.

### Regression tails

Each module below was run separately; no full discovery was run.

| Module (`tests.` prefix) | Exact tail |
|---|---|
| `test_acc_25g83_rev5` | `Ran 12 tests in 17.333s` / `OK` |
| `test_battery_float` | `Ran 55 tests in 52.671s` / `OK` |
| `test_battery_float_consumers` | `Ran 9 tests in 9.972s` / `OK` |
| `test_battery_float_sweep` | `Ran 3 tests in 0.058s` / `OK` |
| `test_calibration_cadence_report` | `Ran 9 tests in 2.326s` / `OK` |
| `test_calibration_exits` | `Ran 48 tests in 502.010s` / `OK` |
| `test_calibration_ledger` | `Ran 95 tests in 7.071s` / `OK (skipped=1)` |
| `test_calibration_ledger_custody` | `Ran 62 tests in 46.839s` / `OK` |
| `test_calibration_live_three_window` | `Ran 23 tests in 3.305s` / `OK (skipped=3)` |
| `test_calibration_writer_crash_matrix` | `Ran 20 tests in 266.225s` / `OK` |
| `test_check_gate_ledger` | `Ran 39 tests in 8.737s` / `OK` |
| `test_epoch_continuation` | `Ran 68 tests in 58.813s` / `OK` |
| `test_epoch_equivalence_check` | `Ran 28 tests in 13.013s` / `OK` |
| `test_gen_state` | `Ran 44 tests in 2.839s` / `OK` |
| `test_issue_calibration_acceptance_generation` | `Ran 156 tests in 172.267s` / `FAILED (failures=1)` |
| `test_paper_anchor_correction_quantified` | `Ran 12 tests in 0.172s` / `OK` |
| `test_paper_round7_artifacts` | `Ran 69 tests in 521.880s` / `OK` |
| `test_powermetrics_fiducial` | `Ran 75 tests in 66.449s` / `OK` |
| `test_preregistration_chain_digest` | `Ran 8 tests in 0.006s` / `OK` |
| `test_revision_five_b_readers` | `Ran 2 tests in 0.004s` / `OK` |
| `test_run_night` | `Ran 237 tests in 148.196s` / `FAILED (failures=1, skipped=9)` |
| `test_t0_rehearsal` | `Ran 32 tests in 17.775s` / `OK` |
| `test_validate_powermetrics_fiducial` | `Ran 12 tests in 9.062s` / `OK` |
| `test_validate_powermetrics_fiducial_derivation_only` | `Ran 27 tests in 207.495s` / `OK` |
| `test_write_derivation_night_inputs` | `Ran 16 tests in 0.794s` / `OK` |

The additional `test_arm_readiness` and `test_git_fixture_maintenance` run ended `Ran 76 tests in 54.740s` / `OK`. The worktree remained clean.

## Residual risk

No live hardware or quiet-window measurement was attempted, as the charge prohibits it.

**FIX-FIRST.**