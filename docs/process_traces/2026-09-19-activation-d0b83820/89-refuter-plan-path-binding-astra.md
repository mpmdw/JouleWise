```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "E1–E5 completed; one confirmed path-normalization regression, plus environmental failures and supervision timeouts.",
  "workspace": {
    "base_requested": "a9e48ae900a608b3254a732fb8e7463d66bdef1e",
    "base_mode": "exact",
    "head_start": "9a0d8fa853cbdbad1177a0588891b23d4966d225",
    "head_end": "9a0d8fa853cbdbad1177a0588891b23d4966d225",
    "upstream_end": "9a0d8fa853cbdbad1177a0588891b23d4966d225",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 1, "nit": 0},
    "findings": [
      {
        "id": "R1",
        "severity": "should_fix",
        "title": "Resolved installer paths fail the new lexical comparison",
        "location": "joulewise/night_agent_install.py:897",
        "call_site": "main:1185 resolves args.plan; Prepared.render:610 emits the resolved published path; evidence_probe_bindings:898 compares it against unresolved custody_root. scripts/gen_evidence_night.py:48 also leaves custody_root unresolved.",
        "counterfactual": "Using real base implementations, a published plan with custody_root under /tmp passes bindings when supplied through its resolved /private/tmp path. At HEAD, real staged rendering, atomic publication, and Prepared.render produce a published --plan that real bindings refuse with 'evidence plan not at its published path'. Both paths identify the same file.",
        "recommendation": "Use one consistent canonical published-path derivation across generation and installation; add coverage using an aliased custody root and the actual rendered --plan."
      }
    ],
    "E2": "Canonical-root fixture: real Prepared.render gives both jobs the same published path exported by the wrapper; real verify_environment succeeds after staging disappears. Static chain: plist template passes --plan; run_night.py:2940 resolves and reads it, then executes plan.chain_path; quiet_predicate_evidence.zsh:7 requires EVIDENCE_PLAN_PATH; quiet_predicate_campaign.py:95 and :555 read that export. No staged-path consumer remains. Aliased custody roots expose R1.",
    "E3_exports": {
      "NIGHT_PAYLOAD_KIND": "Fixed generator constant; not argument-derived.",
      "PYTHONDONTWRITEBYTECODE": "Fixed generator constant; not argument-derived.",
      "EVIDENCE_PLAN_PATH": "Content-derived: custody_root plus night_plan.json.",
      "EVIDENCE_MANIFEST_PATH": "Content-derived: chain_path sibling; --out must match chain_path.",
      "EVIDENCE_MANIFEST_SHA256": "Content-derived: sealed manifest bytes.",
      "EVIDENCE_CHAIN_SOURCE_SHA256": "Content-derived: tracked chain digest in manifest.",
      "PY": "Content-derived: measurement_root plus /.venv/bin/python.",
      "PYTHONPATH": "Content-derived: measurement_root."
    },
    "E3_other_literals": "No other argument-derived emitted literal is compared with a runtime path. Identity guards and execution paths derive from plan content or constants.",
    "E4_method": "Read original seat-87 checker and helpers; replayed with this head, a /tmp measurement facade, and obsolete blocker assertions replaced with positive assertions in memory. Original receipt/plist mocks retained; generator and publication bindings remained real. No source files changed.",
    "E5_test_audit": "No tests or assertions deleted or weakened. Diff adds three regressions and changes the shared fixture filename from plan.json to night_plan.json."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/ppref-d0b83820-review/e1.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PASS staging author -> real generator --render-only; export is <custody>/night_plan.json",
          "PASS staged probe before publication: evidence plan not at its published path",
          "PASS os.replace -> real evidence_probe_bindings; plan SHA and published input digest match",
          "PASS removed staged probe after publication: evidence plan not at its published path",
          "PASS custody_root differs from plan directory: evidence plan not at its published path",
          "PASS staged wrapper bytes == published wrapper bytes (all four artifacts identical)",
          "PASS driver and deadman rendered --plan == executor EVIDENCE_PLAN_PATH; real verify_environment reads published plan with staging absent"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "real verify_environment reads published plan with staging absent"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/ppref-d0b83820-review/dry-replay.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PASS fixture publication preserves bytes and real published probe bindings pass",
          "PASS synthetic receipt validator: schema, verify-only, no collect/load, cleanup, <6 h freshness",
          "PASS actual step5 assertions on synthetic plists; wrong schedule/argv/root/RunAtLoad refuse",
          "DRY CHECK COMPLETE: fixture checks passed; staging/publication binding repaired"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "staging/publication binding repaired"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp JOULEWISE_CUSTODY_PARENT=/tmp/ppref-d0b83820-review/custody JOULEWISE_ADDITIONAL_CUSTODY_PARENTS='[]' /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v tests.test_gen_evidence_night tests.test_night_agent_install tests.test_night_gate tests.test_run_night tests.test_quiet_predicate_campaign",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 392 tests in 1294.884s", "", "FAILED (failures=4, skipped=9)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B scripts/quick_suite.py --tier quick --workers 4",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["QUICK SUMMARY tier=quick modules=153 excluded=89 failures=1 seconds=122.999 result=FAIL"]
      },
      "expected": {"exit_code": 0, "tail_regex": "result=PASS"}
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/ppref-d0b83820-review/alias-repro.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "BASE real bindings at installer-normalized published path: PASS",
          "HEAD real Prepared.render supplies resolved published --plan to both jobs",
          "HEAD real bindings at installer-normalized published path: evidence plan not at its published path",
          "CONFIRMED regression: custody_root starts /tmp; installer resolves --plan to /private/tmp; the same published file is refused at HEAD"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "CONFIRMED regression"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v tests.test_run_night.BindSupervisionProcessTests.test_blocking_join_startup_and_post_publication tests.test_run_night.BindSupervisionProcessTests.test_startup_hang_is_nonblocking",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 2 tests in 16.016s", "", "FAILED (failures=2)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V7",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B scripts/fixture_orphan_census.py --fail-on-orphans",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": ["{\"error\": \"PermissionError: [Errno 1] Operation not permitted: 'ps'\"}"]
      },
      "expected": {"exit_code": 0, "tail_regex": ".*"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Process-list restrictions explain tests.test_night_agent_install.LaunchdAccessProbeTests.test_cleanup_refusal_reports_the_failure_it_interrupted (pgrep: Cannot get process list), and tests.test_axi_controller_events.AxiControllerEventTests.test_campaign_prebundle_process_failure_retains_identity_receipt_and_row plus test_campaign_zero_exit_without_finalized_bundle_is_dispatch_failure (campaign start identity unavailable via /bin/ps). Direct /bin/ps and the orphan census were denied.",
      "needs": "Rerun these tests and the census with process-list access."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Three BindSupervisionProcessTests failed the external eight-second watchdog: test_blocked_journal_never_blocks_deadline_or_grants_go, test_blocking_join_startup_and_post_publication, and test_startup_hang_is_nonblocking. Journal also failed individually (1 test, 8.013s); both startup tests failed their independent replay. Driver, test, and supervision-fixture files are unchanged from base. These failures are not established as patch regressions.",
      "needs": "Lead adjudicates the supervision timeouts before treating broader verification as green."
    }
  ]
}
```

## Findings

**R1 — should fix:** The new comparison at [night_agent_install.py:897](/Users/edr/code/JouleWise-wt-ppref-d0b83820/joulewise/night_agent_install.py:897) rejects valid published paths after installer normalization. `/tmp/...` versus `/private/tmp/...` reproduces this with real implementations: base passes, head refuses.

Use a consistent canonical path in generation and installation, then add a regression through the real plist renderer. Canonical-root publication works; E4’s adapted replay contains no `CONFIRMED BLOCKER` lines.

## Residual risk

Broader verification remains red for the named census and supervision failures. Fixture cleanup could not be independently censused because `ps` was blocked. No live hardware or installation validation was performed.

The worktree remains clean at the requested head. Scripts and logs are retained in `/tmp/ppref-d0b83820-review/`.