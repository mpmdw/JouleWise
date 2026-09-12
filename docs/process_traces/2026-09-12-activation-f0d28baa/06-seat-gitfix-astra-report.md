```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Migrated the remaining eligible fixture to the shared helper and strengthened the enumeration guard; all touched modules passed three consecutive runs.",
  "workspace": {
    "base_requested": "ace4cc3c",
    "base_mode": "exact",
    "head_start": "ace4cc3cf545728e7327c14ba1084cbabb47e3ad",
    "head_end": "ace4cc3cf545728e7327c14ba1084cbabb47e3ad",
    "upstream_end": "ace4cc3cf545728e7327c14ba1084cbabb47e3ad",
    "branch": "fix/2026-09-12-git-fixture-maintenance-sweep"
  },
  "pathspec": [
    "tests/test_git_fixture_hygiene.py",
    "tests/test_git_fixture_maintenance.py",
    "tests/test_identity_pins.py"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_git_fixture_hygiene -q",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK\\s*$"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_git_fixture_maintenance -q",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK\\s*$"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_identity_pins -q",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK\\s*$"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_git_fixture_hygiene.GitFixtureHygieneTests.test_repository_census -q",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (failures=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=1\\)"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_git_fixture_hygiene.GitFixtureHygieneTests.test_repository_census -q",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK\\s*$"}
    },
    {
      "id": "V6",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Hosted verification across both interpreters remains outstanding.",
      "needs": "Magistrate reviews the diff and obtains the required green hosted run."
    }
  ]
}
```

## Change

The baseline already contained most migrations and an enumeration guard. Identity-pins now imports the shared controls and calls the ONE shared initializer, `tests/git_fixture.py:17`; its tuple is at `:9`, raw initialization at `:26`. Existing assertion ASTs are unchanged.

Guard design: The recursive AST census resolves literal command assignments and aliases and detects argv, wrapper, shell-string, and f-string initialization forms without executing scanned modules. It requires shared-helper routing or established local hygiene with the exact tuple, and restricts maintenance-on exceptions to the two named calibration tests with the kernel fence citation.

Final enumeration—48 shared-helper calls; comma-separated numbers identify separate lines:

```text
tests/fixtures/epoch_bootstrap/build.py:137
tests/test_arm_readiness.py:191
tests/test_arm_readiness_evidence.py:270,594
tests/test_arm_readiness_lifecycle.py:506,1037,1359
tests/test_arm_readiness_pack_digest.py:33
tests/test_bridge.py:123
tests/test_bundle.py:204
tests/test_calibration_bracketing.py:970
tests/test_calibration_ledger.py:146
tests/test_calibration_live_three_window.py:177,1368
tests/test_calibration_writer_crash_matrix.py:354
tests/test_check_gate_ledger.py:41
tests/test_d117_contrast_v5_pack.py:364
tests/test_d117_decode_contrast_plan.py:307
tests/test_d117_floor_qwen25_1p5b_plan.py:169
tests/test_d117_floor_qwen25_7b_plan.py:160
tests/test_family_marker.py:931,1406
tests/test_gen_derivation_night.py:124
tests/test_git_fixture_maintenance.py:253
tests/test_identity_pins.py:73
tests/test_install_magistrate_watchdog.py:107,124
tests/test_install_night_agent.py:34
tests/test_issue_dg071_dg075_statistics.py:261,878,1042,1191
tests/test_launch_window.py:1238
tests/test_magistrate_watchdog.py:2080
tests/test_magistrate_watchdog_cli.py:38
tests/test_mint_floor_artifact_generalized.py:4614
tests/test_paper_custody.py:201
tests/test_paper_reported_energy.py:273
tests/test_reauthor_clean.py:86
tests/test_receipt_histsem.py:658,1011,1702,2071
tests/test_rehearse_t0_unattended.py:80
tests/test_run_night.py:71
tests/test_s0_line_audit_guard.py:105
tests/test_scheduler_gates.py:576
tests/test_validate_powermetrics_fiducial_derivation_only.py:257
```

Identity-pins wrapper callers: `tests/test_identity_pins.py:524,570,632,1355,1479,1657`.

Remaining raw-init sites:

```text
tests/git_fixture.py:26 — shared implementation
tests/test_calibration_exits.py:2146 — _configure_fixture_repo
tests/test_calibration_exits.py:3650 — PublicGovernedExitWitnessTests.setUp
```

**Deferred sites:** Both calibration-exits sites already carry the full tuple; migration was deferred because the entire file is fenced. Its wrapper callers are at `:2160,2699`. No Git-init sites were found in the other four fenced files.

The explicit maintenance-on exception names are:

- `CalibrationExitReliabilityTests.test_minimal_git_create_commit_cleanup_cycles_are_bounded`
- `CalibrationExitReliabilityTests.test_forced_auto_maintenance_mutation_reproduces_cleanup_race`

The guard cites `docs/process_traces/2026-08-26-t26-ci-reliability/README.md`, “What this cure does NOT cover, and the row that would.” Synthetic source strings in the guard tests are scanned as data and never create repositories.

Killed cut: replaced the migrated identity-pins helper call with raw `git(root, "init", "-q")`, removing that site's tuple installation. The guard identified `test_identity_pins.py:73`.

```text
KILLED_CUT: guard FAILS; exit=1
RESTORED: guard PASS; exit=0
SHA256_BEFORE=718bcbace9d3ccf586d40c728b1034640fba9da766b32d5e48000ebed5b7936d
SHA256_AFTER=718bcbace9d3ccf586d40c728b1034640fba9da766b32d5e48000ebed5b7936d
```

Three consecutive runs per module, using V1–V3:

```text
test_git_fixture_hygiene #1: Ran 5 tests in 5.656s — OK
test_git_fixture_hygiene #2: Ran 5 tests in 5.706s — OK
test_git_fixture_hygiene #3: Ran 5 tests in 5.730s — OK
test_git_fixture_maintenance #1: Ran 5 tests in 5.823s — OK
test_git_fixture_maintenance #2: Ran 5 tests in 5.837s — OK
test_git_fixture_maintenance #3: Ran 5 tests in 5.835s — OK
test_identity_pins #1: Ran 42 tests in 10.580s — OK
test_identity_pins #2: Ran 42 tests in 10.972s — OK
test_identity_pins #3: Ran 42 tests in 10.521s — OK
```

`git status --short`:

```text
 M tests/test_git_fixture_maintenance.py
 M tests/test_identity_pins.py
?? tests/test_git_fixture_hygiene.py
```

`git diff --stat`:

```text
 tests/test_git_fixture_maintenance.py | 113 +++++++++++++++++++++++++++++++---
 tests/test_identity_pins.py           |  14 +----
 2 files changed, 107 insertions(+), 20 deletions(-)
```

The untracked new guard module adds 75 lines and is absent from that stat. No commit or push; HEAD unchanged. No NEEDS_SCOPE or NEEDS_RULING.

## Verification notes

Pytest is unavailable, so verification used unittest. Full discovery was not run for this fixture/test-tooling-only change; all required targeted repetitions passed.

During development, an uncached scanner run was interrupted for excessive runtime, and two exception-handling subtests failed. Cached lexical bindings and corrected exception handling resolved these before the reported three-pass runs.

## Residual risk

The static guard covers the enumerated command forms; arbitrary dynamically synthesized commands remain outside its analysis. Next step: magistrate diff review and the required hosted run across both interpreters.