```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "FIX-FIRST: tested admission paths refuse correctly, but the primitive guard is bypassable and the required pin proof is nonempty.",
  "workspace": {
    "base_requested": "a44f0685",
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
        "severity": "should_fix",
        "title": "Relative imports evade the primitive-reference guard",
        "path": "tests/test_battery_float_consumers.py",
        "line": 82,
        "evidence": "V2: from . import battery_float as rbf followed by rbf.validate_window(s) produces zero violations."
      },
      {
        "id": "R2",
        "severity": "should_fix",
        "title": "The mandated empty pin proof fails after the main merge",
        "path": "configs/calibration/preregistration_d079_epoch_25g83_rev1.md",
        "line": 600,
        "evidence": "V3: 20 insertions and 2 deletions, from the merged registration seal and A-R5b append."
      },
      {
        "id": "R3",
        "severity": "nit",
        "title": "The primitive loader still accepts an absent registration digest",
        "path": "joulewise/battery_float.py",
        "line": 593,
        "evidence": "V2: a committed record missing preregistration_sha256 loads with None and returns pass; the public seam correctly refuses."
      },
      {
        "id": "R4",
        "severity": "nit",
        "title": "The authoritative obligations reissue remains unlanded",
        "path": "docs/process_traces/2026-09-25-activation-ed17a643/bfg-d/25-seat-report-r7.md",
        "line": 132,
        "evidence": "The report explicitly says the reissue is not landed; 06-harvest-final-obligations-v1.1-source.md section 4.5 still prescribes primitive calls and the removed continuation gate."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/bfgd-final-astra/sweep.py",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 0, "tail": ["SWEEP_DONE 43 FAILED 2"]},
      "expected": {"exit_code": 0, "tail_regex": "SWEEP_DONE 43 FAILED 0"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/bfgd-final-astra/probes.py > /tmp/bfgd-final-astra/probes.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["PROBES_DONE"]},
      "expected": {"exit_code": 0, "tail_regex": "PROBES_DONE"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --stat c6814dd8 a44f0685 -- joulewise/calibration_bracketing.py joulewise/adapters/powermetrics.py joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/reduce.py protocol_v3.json scripts/night_chains configs scripts/paper_anchor_correction_quantified.py",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 0, "tail": [" 1 file changed, 20 insertions(+), 2 deletions(-)"]},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --exit-code c6814dd8 a44f0685 -- scripts/paper_anchor_correction_quantified.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_run_night.BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go > /tmp/bfgd-final-astra/watchdog-current.log 2>&1",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 1 test in 8.007s", "FAILED (failures=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/bfgd-final-astra/watchdog_baseline.py",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 1 test in 8.007s", "FAILED (failures=1)", "BASELINE_EXIT 1"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "/usr/sbin/sysctl -n kern.osversion",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["sysctl: sysctl fmt -1 1024 1: Operation not permitted"]},
      "expected": {"exit_code": 0, "tail_regex": ".+"}
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "git status --short --branch --untracked-files=all && git rev-parse HEAD && git diff --stat a44f0685 HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)", "3ad48d1e52451914aeca30f583bea1f5bdd31b34", " 1 file changed, 34 insertions(+)"]},
      "expected": {"exit_code": 0, "tail_regex": "HEAD \\(no branch\\)"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The literal pin requirement conflicts with the merged registration changes.",
      "needs": "Authorize a narrowly scoped exception for commits 23dd9909 and ad7565a7, or provide the intended post-merge baseline; rerun the agreed pin proof."
    },
    {
      "id": "G2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The issuer live-identity test fails because the sandbox denies sysctl. Its test and observe_machine are unchanged from 3e984ecc.",
      "needs": "Lead verifies the live-identity test where the required read-only access is available."
    },
    {
      "id": "G3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The blocked-journal watchdog test fails at both current HEAD and 3e984ecc in this environment; the sweep is not wholly green.",
      "needs": "Lead retains and investigates this pre-existing verification failure; do not erase it with the passing battery results."
    }
  ]
}
```

## Findings

No BLOCKER reproduced in the current admission paths.

**R1 — MATERIAL: relative imports bypass the AST guard.**  
In a `/tmp` copy of `joulewise/night_gate.py`, adding `from . import battery_float as rbf` and `rbf.validate_window(s)` produces **zero violations**. The [guard](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-astra/tests/test_battery_float_consumers.py:82) does not resolve relative imports. A new consumer can therefore call a primitive without the required guard failure. Resolve relative imports and add a regression.

Executed mutation results:

| Mutation | AST result | Behavioral result |
|---|---|---|
| Qualified direct primitive call | 1 violation | Rejected structurally |
| Catch refusal and continue | 0 violations | Existing behavioral expectations fail |
| Collect named sessions only | 0 violations | Existing behavioral expectations fail |
| Relative-import primitive call | 0 violations | Guard gap confirmed |

The stronger zero-valid-row fixture demonstrates why the behavioral checks matter: current code returns **check 5 / prepare 3** after custody tampering; both control-flow mutants return **0 / 0**, including false “admissible.” These results apply to the temporary mutants, not current production code. [Executed probes](/tmp/bfgd-final-astra/probes.log).

**R2 — MATERIAL: the required pin proof is nonempty.**  
The exact charge command reports **20 insertions, 2 deletions** in the preregistration. These come from the main-merge seal and A-R5b append. The other pinned paths match, including the paper producer. The lead must reconcile the required baseline or authorize an explicit exception before this gate can pass.

**R3 — NIT: the loader’s missing-digest guarantee is incomplete.**  
A committed record with `preregistration_sha256` omitted loads successfully when passed `None`, returning `pass`. The [comparison](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-astra/joulewise/battery_float.py:593) accepts `None == None`. Validate the argument independently. The public seam correctly rejects this input, so no current consumer bypass was reproduced.

**R4 — NIT: finish the obligations reissue.**  
The [seat report](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-astra/docs/process_traces/2026-09-25-activation-ed17a643/bfg-d/25-seat-report-r7.md:132) explicitly leaves §4.5 “not landed.” Its source still prescribes direct primitive calls and the removed continuation gate. Install and link the authoritative reissue.

**Positive executed evidence:** P3 refuses A-7 on both tools; declared P4 admits on both; undeclared/overlapping/clean declarations refuse on both; P5 control and uncommitted-pin cases agree. F1 deletion and tampering refuse as custody failures; byte-exact restoration returns A-7 on both. Additional mirrored-refusal probes also agreed. Both consumers use the shared collector, policy, and target epoch. The consumer re-grep found no additional current verdict-deciding path outside the seam.

H-2 determinism and anchor non-overlap passed. Three fixture-option invocations outside logical/direct sampler mode each exited **2**, with `battery probe fixture requires the logical sampler test mode`. H-4’s paper producer is byte-identical to `c6814dd8`.

The importer sweep ran **43 modules, 2,656 tests: 2,634 passed, 20 skipped, 2 failed**. No full discovery was run. Exact unittest summaries follow; module names have the `tests.` prefix.

| Module | Executed summary |
|---|---|
| test_battery_float_consumers | Ran 9 tests in 10.230s; OK |
| test_battery_float | Ran 55 tests in 52.917s; OK |
| test_issue_calibration_acceptance_generation | Ran 156 tests in 185.618s; FAILED (failures=1) |
| test_calibration_exits | Ran 48 tests in 535.646s; OK |
| test_validate_powermetrics_fiducial_derivation_only | Ran 27 tests in 209.769s; OK |
| test_acc_25g83_rev5 | Ran 12 tests in 17.188s; OK |
| test_arm_readiness | Ran 71 tests in 41.489s; OK |
| test_arm_readiness_evidence_t0 | Ran 78 tests in 414.012s; OK (skipped=5) |
| test_arm_readiness_lifecycle | Ran 69 tests in 108.289s; OK (skipped=1) |
| test_arm_readiness_schemas | Ran 50 tests in 0.673s; OK |
| test_battery_float_sweep | Ran 3 tests in 0.057s; OK |
| test_calibration_cadence_report | Ran 9 tests in 2.438s; OK |
| test_calibration_ledger | Ran 95 tests in 7.919s; OK (skipped=1) |
| test_calibration_ledger_custody | Ran 62 tests in 51.421s; OK |
| test_calibration_live_three_window | Ran 23 tests in 3.822s; OK (skipped=3) |
| test_calibration_writer_crash_matrix | Ran 20 tests in 297.371s; OK |
| test_check_gate_ledger | Ran 39 tests in 13.189s; OK |
| test_cli_run | Ran 130 tests in 60.573s; OK |
| test_d078_reason_registry | Ran 14 tests in 0.081s; OK |
| test_detection_floor | Ran 161 tests in 23.545s; OK (skipped=1) |
| test_epoch_continuation | Ran 68 tests in 57.685s; OK |
| test_epoch_equivalence_check | Ran 28 tests in 14.691s; OK |
| test_evidence_night | Ran 161 tests in 423.902s; OK |
| test_floor_extraction | Ran 170 tests in 23.347s; OK |
| test_gen_state | Ran 44 tests in 3.236s; OK |
| test_git_fixture_hygiene | Ran 7 tests in 0.015s; OK |
| test_git_fixture_maintenance | Ran 5 tests in 6.819s; OK |
| test_install_night_agent | Ran 65 tests in 137.642s; OK |
| test_launch_window | Ran 38 tests in 520.771s; OK |
| test_night_gate | Ran 104 tests in 1.472s; OK |
| test_paper_anchor_correction_quantified | Ran 12 tests in 0.349s; OK |
| test_paper_excursion_decomposition | Ran 13 tests in 0.325s; OK |
| test_paper_round7_artifacts | Ran 69 tests in 469.664s; OK |
| test_powermetrics_fiducial | Ran 75 tests in 66.612s; OK |
| test_preregistration_chain_digest | Ran 8 tests in 0.005s; OK |
| test_rehearse_t0_unattended | Ran 8 tests in 3.630s; OK |
| test_revision_five_b_readers | Ran 2 tests in 0.004s; OK |
| test_run_campaign | Ran 293 tests in 338.333s; OK |
| test_run_night | Ran 237 tests in 163.063s; FAILED (failures=1, skipped=9) |
| test_t0_rehearsal | Ran 32 tests in 17.441s; OK |
| test_validate_powermetrics_fiducial | Ran 12 tests in 9.004s; OK |
| test_whole_window | Ran 58 tests in 21.787s; OK |
| test_write_derivation_night_inputs | Ran 16 tests in 0.761s; OK |

## Residual risk

The issuer failure is the sandbox-denied live identity probe. The night-driver watchdog failure reproduced both in isolation and at `3e984ecc`; its cause remains unresolved. Neither failure is concealed by the passing battery tests.

No live hardware validation was performed. H-4’s paper exemption was evaluated within its specified historical-input scope. The repository remained clean and HEAD unchanged.

**FIX-FIRST**