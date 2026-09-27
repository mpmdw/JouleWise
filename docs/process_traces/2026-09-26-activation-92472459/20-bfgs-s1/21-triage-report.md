```json
{
  "schema": "claude-codex-report/v1",
  "genre": "root_cause",
  "status": "findings",
  "completion": "complete",
  "summary": "V2 needs a four-site typed guard ruling; V3 has 82 battery-gate failures, four baseline AXI failures, and one collateral paper-source pin failure.",
  "workspace": {
    "base_requested": "1417c0c4caf36f7ac132410b3cd3ebc7aefbd9e7",
    "base_mode": "descendant",
    "head_start": "24b79db349706c9945ce42789b1be862a4400edc",
    "head_end": "24b79db349706c9945ce42789b1be862a4400edc",
    "upstream_end": "24b79db349706c9945ce42789b1be862a4400edc",
    "branch": "feat/2026-09-26-bfgs-s1-bundles"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "cause": "confirmed",
    "remediation": "proposed"
  },
  "verification": [
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.test_battery_float tests.test_battery_float_consumers tests.test_evidence_night tests.test_night_kinds",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 312 tests in 852.868s",
          "",
          "FAILED (failures=2)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 312 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V3-head",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.test_analysis_integration tests.test_audit_amplification tests.test_audit_bundle_validation tests.test_authentication_io tests.test_axi_controller_events tests.test_axi_mock_spec tests.test_axi_request_validation tests.test_cli tests.test_cli_run tests.test_corpus_strict_validation tests.test_determinism_gate tests.test_envelope_gate tests.test_experiment tests.test_floor_extraction tests.test_gate_sensibility_rounding tests.test_idle_dependence tests.test_mint_floor_artifact_generalized tests.test_nvidia_node_integration tests.test_p2038_production_path tests.test_package_bundle_pack tests.test_paper_reported_energy tests.test_partial_record_enclosure tests.test_phase_share tests.test_powermetrics tests.test_report tests.test_rpt001_report_slice tests.test_schemas tests.test_whole_window_selection tests.test_window_duration_margins",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 1052 tests in 533.752s",
          "",
          "FAILED (failures=50, errors=37, skipped=16)",
          "KILLED 3 renderer AST mutations: wrapper deletion, widened annotation, unregistered renderer"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1052 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V3-base-failures",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp PYTHONPATH=. python3 /tmp/bfgs_s1_rerun_failed.py",
      "cwd": "/tmp/bfgs-s1-base-1417c0c4",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 78 tests in 510.589s",
          "",
          "FAILED (failures=4, errors=1)",
          "RESULT 78 4 1 0",
          "ERROR tests.test_rpt001_report_slice.TestRpt001Artifacts.test_full_route_census_emits_only_void_artifacts subprocess.CalledProcessError: Command '['git', 'ls-files', '-z']' returned non-zero exit status 128."
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "RESULT 78 4 1 0"
      }
    },
    {
      "id": "V3-base-RPT001-with-temp-Git",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.test_rpt001_report_slice.TestRpt001Artifacts.test_full_route_census_emits_only_void_artifacts",
      "cwd": "/tmp/bfgs-s1-base-1417c0c4",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          ".",
          "----------------------------------------------------------------------",
          "Ran 1 test in 11.698s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test in .*s\\n\\nOK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The S0 exact replacement-site guard sees four pre-existing controller calls after S1 imports battery_float.",
      "needs": "Rule the typed four-site allowlist update, or a closed battery-integration split, and grant the guard test path."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The production RPT001 figure route refuses six retained non-MOCK bundles whose complete digests are absent from the ruled historical set.",
      "needs": "Cold-gate historical admission or an explicit decision that the full route must refuse pending HISTORICAL-BATTERY-STATE-01."
    },
    {
      "id": "F3",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "No failing V3 test module is literally in S1 Final texts v1.1 §E's write allowlist.",
      "needs": "Issue exact prospective test-path scope before compatibility fixes."
    },
    {
      "id": "F4",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "Four AXI identity failures recur at base; one paper custody fixture has a stale source-bound receipt after bundle_read changed.",
      "needs": "Handle outside the battery reader fix."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "tests/test_battery_float_consumers.py",
      "tests/test_analysis_integration.py",
      "tests/test_floor_extraction.py",
      "tests/test_whole_window_selection.py",
      "tests/test_window_duration_margins.py",
      "tests/test_run_campaign.py",
      "tests/test_audit_amplification.py",
      "tests/test_cli.py",
      "tests/test_cli_run.py",
      "tests/test_p2038_production_path.py",
      "tests/test_package_bundle_pack.py",
      "tests/test_partial_record_enclosure.py",
      "tests/test_phase_share.py",
      "tests/test_powermetrics.py",
      "tests/test_rpt001_report_slice.py"
    ],
    "reason": "These exact test paths are outside the ruled S1 write allowlist and contain the guard or battery-gate compatibility cases.",
    "blocked_work": "Make V2 and S1-induced V3 cases green without weakening the gate.",
    "minimal_change": "Add four type-justified exact guard sites; repair synthetic bundle and capture evidence and update superseded expectations. RPT001 historical admission needs a separate cold-gate ruling."
  }
}
```

## Causal chain

### Q1 — F1 guard

The executed AST census found these four calls in [controller.py](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/joulewise/controller.py:1983). `git show 1417c0c4:joulewise/controller.py | rg -n 'events.append\(replace|sub_config = replace|sampling=replace|member_config = replace'` showed the same calls at base lines **1944, 2504, 2507, 2904**.

| Head site | Replaced value | Can it be or contain `PairVerdict`? |
|---|---|---|
| 1983, `_Execution._axi_request_events` | `RuntimeEvent` | It cannot itself be a `PairVerdict`. Its `metadata: dict[str, Any]` could hold one in unconstrained Python, but this function constructs metadata from AXI scalar/JSON fields. This replacement adds an ordinal; it does not replace a nested verdict. |
| 2566, `cooldown_gate` | `BenchmarkConfig` | A valid schema-derived config contains `SamplingConfig` and config fields, not a verdict. |
| 2569, `cooldown_gate` | `SamplingConfig` | Its three fields are numeric sampling settings; no verdict. |
| 2966, `run_experiment` | `BenchmarkConfig` | Same valid-config constraint; this replacement changes `run_id`. |

The executable predicate in [test_battery_float_consumers.py](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/tests/test_battery_float_consumers.py:206) sets `imports_battery_float = bool(self.module_aliases or self.package_aliases or self.direct_battery_import)`. For such modules it records each `dataclasses.replace`, `copy.replace`, or `__replace__` call as `(path, enclosing qualname, ast.unparse(call))`, flags sites absent from `REPLACE_CALL_ALLOWLIST`, and asserts `Counter(sites) == Counter(REPLACE_CALL_ALLOWLIST.keys())` and `len(REPLACE_CALL_ALLOWLIST) == 9`. This implements Final texts v1.1 text 4’s S0 guard, addendum 2 amendment 25’s named factory exemption, and addendum 3 S-2’s widened replacement detection. The four controller calls became visible solely because S1 added its `battery_float` import.

**Compliant choices:** add four exact, type-described allowlist rows and change the asserted count to 13; replace these four calls with explicit constructors; or move battery operations into a scanned, verdict-closed helper with no replacement calls and no `PairVerdict` returned to controller. A type-aware static guard could also prove these calls’ receiver types, but is a larger guard change. I recommend the **exact four-site allowlist**, with a self-test that `replace(verdict, status='pass')` in controller remains flagged. Its AST match retains detection of a new or edited forgery call. A broad controller exemption, dynamic import used to hide the module, or moving a generic replacement helper outside the guarded module set while verdicts can reach it would **evade** the guard.

### Q2 — F2 V3

I extracted base with `git archive 1417c0c4 | tar -x -C /tmp/bfgs-s1-base-1417c0c4`. Its output tail was `1417c0c4caf36f7ac132410b3cd3ebc7aefbd9e7` and `archive_ready`. The full head log is [here](/tmp/bfgs_s1_v3_head_24b79db3.log); the base failure-method log is [here](/tmp/bfgs_s1_v3_base_1417c0c4.log). The seat indexed 88 cases; committed head has **87**. The old authentication-I/O failure was fixed before commit and its focused rerun passed (`Ran 1 test in 0.923s`, `OK`).

| Class | Seat → committed head | Every affected module at head (case count) | Root cause, representative ID, smallest fix |
|---|---:|---|---|
| **A** | 13 → **14** | `test_analysis_integration` 1; `test_cli` 1; `test_floor_extraction` 5; `test_partial_record_enclosure` 1; `test_rpt001_report_slice` 1; `test_whole_window_selection` 5 | A copied or synthetic non-MOCK bundle has no pair and its completed digest is outside text 8’s closed set. Examples: `test_reduce_default_replays_recorded_060_and_051_versions`, `test_bracket_max_exceeding_minted_member_bound_refuses`. Supply passing pairs through the owning fixture helpers in `tests/test_run_campaign.py`, `tests/test_floor_extraction.py`, and `tests/test_whole_window_selection.py`; adapt the copied-bundle tests. RPT001 is the real retained-bundle exception requiring the ruling below. |
| **B** | 68 → **68** | `test_audit_amplification` 4; `test_cli_run` 25; `test_p2038_production_path` 9; `test_package_bundle_pack` 1; `test_phase_share` 3; `test_powermetrics` 1; `test_whole_window_selection` 1; `test_window_duration_margins` 24 | **47** fixtures lack a digest-bound MOCK config or matching `metadata.config_sha256` (text 8); **11** non-MOCK controller fixtures omit a passing injected probe (texts 7/8); **10** calibration fixtures omit capture pair evidence (text 11). Examples: `test_hand_computed_numeric_oracle` errors with `config.json digest does not match metadata.config_sha256`; `test_real_powermetrics_evidence_path_passes_p2029_p2040_gates` errors with `instrument calibration battery_float_evidence_missing`. Fix the shared constructors in the named test files: write matching config hashes or MOCK config, inject the existing `tests/battery_float_fixture.py` runner, and have capture fixtures write the pair and raw files before sealing `instrument_evidence.json`. |
| **C** | 1 → **0** | None at committed head | The seat’s `test_marked_v2_surface_has_no_direct_readable_io` caught direct `read_bytes` in the historical loader. The committed `read_authentication_input` correction passes. No remaining V3 case establishes an unruled S1 production behavior defect. |
| **D** | 6 → **5** | `test_axi_controller_events` 2; `test_axi_mock_spec` 2; `test_paper_reported_energy` 1 | The four AXI cases fail at **both** commits with `campaign start identity unavailable`; they need a suitable process-identity environment or test injection, not an S1 reader change. The paper case’s `stale supply-map receipt digest: reported_energy_parents` is source-hash collateral from changed `bundle_read.py`; refresh `configs/paper_supply/supply_map.json` after S1 source freeze. The seat’s old RPT001 missing-file result was a pre-commit clone artifact; at committed head it moves to A’s actual prospective refusal. |

The base selected run’s exact summary was `Ran 78 tests in 510.589s`, `FAILED (failures=4, errors=1)`, `RESULT 78 4 1 0`. Its sole error was RPT001’s `git ls-files` call against an archive without Git metadata. After `git init`, `git add -A`, and a snapshot commit **inside `/tmp` only**, that base RPT001 test passed: `Ran 1 test in 11.698s`, `OK`.

**A production route is affected.** [make_figures.py](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/scripts/make_figures.py:238) calls `validate_bundle(bundle_dir, strict=True)` on the six retained RPT001 runs. At head it reports `strict: battery_float_evidence_missing: prospective bundle`. The first retained run has no `battery_float` key, uses `powermetrics`, and has complete digest `9fa8c3f02e419d36ceb6fdb6c9ac4c9717c9b9ab1c7345f66a5b4acff988c3a6`; all six digests are absent from the 13-entry historical set. The committed RPT001 manifest pins `bundle_tree_sha256`, a different digest, so text 8 does not admit them. The route was green at base. Restoring it requires a **cold-gate historical admission** under text 8, or a lead decision to retain the refusal pending HISTORICAL-BATTERY-STATE-01. By contrast, the production calibration producer already writes its pair in [validate_powermetrics_fiducial.py](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/scripts/validate_powermetrics_fiducial.py:2629); the P2038 attachment failures are stale synthetic fixtures.

### Q3 — exact scope

An executed comparison of Final texts v1.1 §E with the head V3 log printed `s1_scope_paths 25`, `v3_failing_modules 16`, `literal_overlap []`. The brief’s SPLIT assigns consumer work to round 2, but **none of the older failing V3 test files is literally authorized by §E**.

| Disposition | Exact paths |
|---|---|
| Round-2 subject matter; grant these older test paths explicitly | `tests/test_analysis_integration.py`, `tests/test_floor_extraction.py`, `tests/test_whole_window_selection.py`, `tests/test_window_duration_margins.py`; shared fixture owner `tests/test_run_campaign.py` |
| New S1 compatibility scope, outside either round | `tests/test_audit_amplification.py`, `tests/test_cli.py`, `tests/test_cli_run.py`, `tests/test_p2038_production_path.py`, `tests/test_package_bundle_pack.py`, `tests/test_partial_record_enclosure.py`, `tests/test_phase_share.py`, `tests/test_powermetrics.py`, `tests/test_rpt001_report_slice.py` |
| Current V3 failures needing separate treatment, not battery fixture scope | `tests/test_axi_controller_events.py`, `tests/test_axi_mock_spec.py` (base failures); `tests/test_paper_reported_energy.py` (refresh its source-bound supply-map receipt after S1 stabilizes) |

Round 2 already owns the eight **production** consumers in text 12 plus `joulewise/scored_reduce.py` (text 9) and `joulewise/calibration_bracketing.py` (text 10). Its named new tests are in §E; that does not confer write authority over the older files above. F1 separately requires `tests/test_battery_float_consumers.py`. The RPT001 policy choice may instead require cold-gate changes to the existing S1 historical-set file and its reader SHA pin; scope alone cannot authorize adding those six digests.

### Q4 — isolated V2 rerun

| Command | Exact tail |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.test_battery_float tests.test_battery_float_consumers tests.test_evidence_night tests.test_night_kinds` | `----------------------------------------------------------------------`<br>`Ran 312 tests in 852.868s`<br>blank line<br>`FAILED (failures=2)` |

## Remediation

Rule the four exact guard rows, then grant the prospective test paths in Q3. Repair synthetic evidence at its shared fixture constructors and update tests whose legacy-identity expectations text 8 supersedes. Decide the six retained RPT001 bundles through the cold gate before changing its production route or expected result.

## Disproved alternatives

The four controller replacements were not introduced by S1, and none replaces a `PairVerdict`. The 24b79db3 V3 failures are not a repeat of the seat’s direct-readable-I/O defect. The AXI identity failures reproduce at base. The RPT001 head failure is not merely the seat’s untracked-file clone error: the committed file is present, and the reader now refuses the retained bundle’s unlisted complete digest.

## Residual risk

The guard is syntactic: its exact-site allowlist does not prove arbitrary Python values can never carry a nested verdict. The typed four-site review and a new-forgery self-test should accompany the ruling. No repository file was edited; final `git status --short --branch` was clean at 24b79db3.