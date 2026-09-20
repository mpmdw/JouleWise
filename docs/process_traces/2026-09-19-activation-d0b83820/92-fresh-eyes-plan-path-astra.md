```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"complete",
  "summary":"F1-F4 completed: runtime fixes and all three mutants verified; one new test portability defect; broader suites have sandbox failures.",
  "workspace":{"base_requested":"9a0d8fa853cbdbad1177a0588891b23d4966d225","base_mode":"exact","head_start":"9f452559541dc6ea1113a0c8d7ab0ceef3208917","head_end":"9f452559541dc6ea1113a0c8d7ab0ceef3208917","upstream_end":null,"branch":null},
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{
    "counts":{"blocker":0,"should_fix":1,"nit":0},
    "findings":[{
      "id":"R1",
      "severity":"should_fix",
      "title":"Alias regression assumes macOS /tmp layout and fails on an unaliased root",
      "call_site":"tests/test_night_agent_install.py:1915, EvidencePlanPublicationTests.test_aliased_custody_root_passes_with_the_installer_resolved_plan_path; .github/workflows/ci.yml:134 runs ordinary tests on ubuntu-latest",
      "counterfactual":"On an ordinary Ubuntu /tmp directory, resolve() leaves the fixture path unchanged, so assertNotEqual fails before either binding call. Replayed on macOS by changing only TemporaryDirectory(dir) to the real /private/tmp directory: the same test fails at line 1915.",
      "recommendation":"Create an explicit custody symlink in the fixture, author the plan with that custody_root, and test literal and resolved plan paths. Do not require /tmp itself to be an alias."
    }],
    "F1":"Four-file diff is confined to 90a: resolve both identity operands, preserve unresolved literal, require absolute custody root, add regressions, move unittest.main. N2 remains deferred and N3 retained as ruled. Both literal/resolved bindings pass for an explicit symlink custody_root and /tmp alias. Relative root raises GenerationRefusal with no artifact writes.",
    "F2":"All mutants killed: (a) plan-side absolute() fails test_aliased_custody_root_passes_with_the_installer_resolved_plan_path and test_staged_render_then_atomic_publication_passes_bindings; (b) omitted _require_absolute fails test_relative_custody_root_refuses_at_the_desk; (c) generator resolve() fails the literal assertion in test_staged_and_published_plan_render_identical_bytes on /tmp versus /private/tmp.",
    "F4":"No additional mutually unsatisfiable sibling comparison. main:1190 resolves args.plan before admit:588 and render_probe; identity:903 resolves both sides; literal:905 stays lexical. input_digests:918 and run_night:3475 retain absolute spellings, but installed producer/validator share resolved Prepared.plan_path. Calibration uses one shared helper; pack containment resolves both sides and pack/G7 symlink rejection is explicit policy."
  },
  "verification":[
    {
      "id":"V1","kind":"smoke",
      "cmd":"env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/ppfinal-9f452559/probes.py",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["relative-root GenerationRefusal; zero artifacts written PASS"]},
      "expected":{"exit_code":0,"tail_regex":"PASS|OK"}
    },
    {
      "id":"V2","kind":"test",
      "cmd":"env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v tests.test_gen_evidence_night tests.test_night_agent_install.EvidencePlanPublicationTests tests.test_night_agent_install.EvidenceProbeReceiptTests",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["Ran 16 tests in 28.277s","","OK"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id":"V3","kind":"test",
      "cmd":"env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/ppfinal-9f452559/mutants.py",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["MUTANT a exit 1","FAILED (errors=2)","MUTANT b exit 1","FAILED (failures=1)","MUTANT c exit 1","FAILED (failures=1)"]},
      "expected":{"exit_code":0,"tail_regex":"MUTANT c exit 1"}
    },
    {
      "id":"V4","kind":"test",
      "cmd":"env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/ppfinal-9f452559/unaliased_test.py",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["Ran 1 test in 1.232s","","FAILED (failures=1)","CONFIRMED: unaliased temporary root fails at assertNotEqual before bindings"]},
      "expected":{"exit_code":0,"tail_regex":"CONFIRMED: unaliased"}
    },
    {
      "id":"V5","kind":"suite",
      "cmd":"env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp TEMP=/tmp TMP=/tmp JOULEWISE_CUSTODY_PARENT=/tmp/ppfinal-9f452559/custody JOULEWISE_ADDITIONAL_CUSTODY_PARENTS='[]' /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v tests.test_gen_evidence_night tests.test_night_agent_install tests.test_night_gate tests.test_run_night tests.test_quiet_predicate_campaign",
      "cwd":".",
      "observed":{"result":"fail","exit_code":1,"tail":["Ran 394 tests in 1391.750s","","FAILED (failures=3, skipped=9)"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id":"V6","kind":"suite",
      "cmd":"env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B scripts/quick_suite.py --tier quick --workers 4",
      "cwd":".",
      "observed":{"result":"fail","exit_code":1,"tail":["QUICK SUMMARY tier=quick modules=153 excluded=89 failures=1 seconds=228.574 result=FAIL"]},
      "expected":{"exit_code":0,"tail_regex":"result=PASS"}
    },
    {
      "id":"V7","kind":"other",
      "cmd":"env PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B scripts/fixture_orphan_census.py --fail-on-orphans",
      "cwd":".",
      "observed":{"result":"fail","exit_code":2,"tail":["{\"error\": \"PermissionError: [Errno 1] Operation not permitted: 'ps'\"}"]},
      "expected":{"exit_code":0,"tail_regex":".*"}
    }
  ],
  "flags":[
    {
      "id":"ENV1","kind":"environment","level":"nonblocking",
      "text":"Sandbox denies /bin/ps and process census. Failures: tests.test_night_agent_install.LaunchdAccessProbeTests.test_cleanup_refusal_reports_the_failure_it_interrupted; tests.test_axi_controller_events.AxiControllerEventTests.test_campaign_prebundle_process_failure_retains_identity_receipt_and_row and test_campaign_zero_exit_without_finalized_bundle_is_dispatch_failure. Orphan census cannot establish cleanup.",
      "needs":"Lead retains process-list-capable verification and cleanup census."
    },
    {
      "id":"ENV2","kind":"environment","level":"nonblocking",
      "text":"Sandbox-only per lead: tests.test_run_night.BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go and test_startup_hang_is_nonblocking hit the external 8 s watchdog. test_blocking_join_startup_and_post_publication passed. Lead reports unsandboxed passes.",
      "needs":"Retain lead unsandboxed verification as authoritative for these cases."
    }
  ]
}
```

## Findings

**R1 — should_fix:** [The new assertion](/Users/edr/code/JouleWise-wt-ppref-d0b83820/tests/test_night_agent_install.py:1915) assumes `/tmp` is an alias. On an unaliased root, it fails before exercising bindings. CI uses Ubuntu.

The reproduction changes only the fixture’s temporary-directory location to `/private/tmp`; production code remains untouched. Use an explicit symlink fixture, then rerun the publication tests and CI.

## Residual risk

The requested suites completed with the environmental failures named above. Process-list restrictions prevented an independent orphan census. No live installation or hardware validation was performed.

The worktree remains clean at `9f452559`. Scripts, mutants, and logs are retained in [/tmp/ppfinal-9f452559](/tmp/ppfinal-9f452559).