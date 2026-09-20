```json
{
  "schema":"claude-codex-report/v1",
  "genre":"implementation",
  "status":"findings",
  "completion":"complete",
  "summary":"Implemented shared self-excluding census argv and regressions; native bench verification and baseline test failures remain.",
  "workspace":{"base_requested":"e1e7d6a7","base_mode":"exact","head_start":"e1e7d6a7d4efad2dd9d6c4951478aab64c5c3013","head_end":"e1e7d6a7d4efad2dd9d6c4951478aab64c5c3013","upstream_end":"d28b3cd36ef3f1ebea07ba88ae415b49bf94a625","branch":"fix/2026-09-20-census-self-match"},
  "pathspec":["joulewise/night_gate.py","joulewise/arm_readiness_evidence_t0.py","scripts/gen_derivation_night.py","tests/test_night_gate.py","tests/test_run_night.py","tests/test_arm_census.py","tests/test_quiet_admission.py","tests/test_arm_readiness_evidence_t0.py","tests/test_arm_readiness_schemas.py","tests/test_arm_readiness_integration.py","tests/test_gen_derivation_night.py","tests/test_agent_census_concurrency.py","docs/process/NIGHT_HANDBACK.md"],
  "unowned_dirty":[],
  "verdict":{"implementation":"implemented","acceptance":"pending_verification"},
  "verification":[
    {
      "id":"V1","kind":"suite",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_night_gate tests.test_run_night tests.test_arm_census tests.test_quiet_admission tests.test_arm_readiness_evidence_t0 tests.test_arm_readiness_schemas tests.test_arm_readiness_integration tests.test_gen_derivation_night tests.test_agent_census_concurrency -q",
      "cwd":".",
      "observed":{"result":"fail","exit_code":1,"tail":["Ran 521 tests in 798.640s","FAILED (failures=2, skipped=17)","real 799.54","user 422.94","sys 302.36"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id":"V2","kind":"test",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python - <<'PY'\nimport unittest\nfrom unittest.mock import patch\nfrom joulewise import night_gate\nnames = ['tests.test_night_gate.NightGateTests.test_census_does_not_match_peer_argv', 'tests.test_run_night.NightDriverTests.test_peer_census_reaches_and_completes_chain']\nsuite = unittest.defaultTestLoader.loadTestsFromNames(names)\nwith patch.object(night_gate, 'AGENT_CENSUS_ARGV', ('/usr/bin/pgrep', '-lf', '|'.join(('codex', 'claude', 't3')))):\n    result = unittest.TextTestRunner(verbosity=1).run(suite)\nprint('COUNTERFACTUAL: old constant produced', len(result.failures), 'failures; production constant restored:', night_gate.AGENT_CENSUS_ARGV)\nraise SystemExit(0 if len(result.failures) == 2 and not result.errors else 1)\nPY",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["Ran 2 tests in 0.138s","FAILED (failures=2)","COUNTERFACTUAL: old constant produced 2 failures; production constant restored: ('/usr/bin/pgrep', '-lf', '[c]odex|[c]laude|[t]3')"]},
      "expected":{"exit_code":0,"tail_regex":"old constant produced 2 failures"}
    },
    {
      "id":"V3","kind":"test",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_agent_census_concurrency -v",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["Ran 3 tests in 0.009s","OK (skipped=3)"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id":"V4","kind":"suite",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python scripts/quick_suite.py --tier quick --workers 4",
      "cwd":".",
      "observed":{"result":"fail","exit_code":1,"tail":["QUICK SUMMARY tier=quick modules=153 excluded=91 failures=1 seconds=137.572 result=FAIL"]},
      "expected":{"exit_code":0,"tail_regex":"failures=0 .*result=PASS"}
    },
    {
      "id":"V5","kind":"test",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_run_night.BindSupervisionProcessTests.test_startup_hang_is_nonblocking -q",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["Ran 1 test in 6.519s","OK"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id":"V6","kind":"inspection",
      "cmd":"git diff --check && git diff --stat",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":[" 12 files changed, 106 insertions(+), 18 deletions(-)"]},
      "expected":{"exit_code":0,"tail_regex":"12 files changed"}
    },
    {
      "id":"V7","kind":"inspection",
      "cmd":"git diff --no-index --stat /dev/null tests/test_agent_census_concurrency.py",
      "cwd":".",
      "observed":{"result":"pass","exit_code":1,"tail":[" .../null => tests/test_agent_census_concurrency.py | 198 +++++++++++++++++++++"," 1 file changed, 198 insertions(+)"]},
      "expected":{"exit_code":1,"tail_regex":"198 insertions"}
    }
  ],
  "flags":[
    {"id":"F1","kind":"verification_gap","level":"nonblocking","text":"All three new native tests skipped explicitly: /usr/bin/pgrep unavailable in sandbox: exit 3, Cannot get process list. Existing t0 native census tests now detect the same condition.","needs":"Lead runs V3 at the bench, including the old-pattern overlap control."},
    {"id":"F2","kind":"verification_gap","level":"nonblocking","text":"V1 failed journal_block and startup_hang at their existing 8-second watchdog. Journal failure reproduced with e1e7d6a7 night_gate loaded inside the supervised process; startup passed isolated rerun V5. V4's sole failing module was test_axi_controller_events: two campaign-start-identity assertions also reproduced with baseline production modules.","needs":"Lead adjudicates baseline failures and intermittent startup timeout; broad suites are not green."},
    {"id":"F3","kind":"baseline_drift","level":"nonblocking","text":"origin/main advanced externally by two commits during the session. Worktree HEAD remained at the requested base; no commits, pushes, or branch changes were made.","needs":"Lead accounts for upstream movement before landing."}
  ]
}
```

## Change

The shared argv now uses `[c]odex|[c]laude|[t]3`. The t0 author imports it inside its census function, preserving its closed public namespace. Arm discovery, quiet admission, and watchdog consumption were confirmed unchanged.

Added gate/driver counterfactual regressions and native synchronized, stopped-peer, and agent-marker checks. Updated pins and the legacy receipt comparison’s argv input. `agent_census`, `_check_census`, and executable generator logic are unchanged. Every handbook `## Executed —` block remains byte-identical.

## Verification notes

Both peer regressions failed with the old constant: the gate returned `night_refused_agent_present`, and the driver returned refusal before launching its chain. They pass with the fix; foreign agents still refuse/abort.

The final focused run’s only failures were the two supervision timeouts described in F2. Native skips name the sandbox error. A headless Metal warning also appeared at interpreter shutdown.

The literal sweep retains:

- `joulewise/t0_rehearsal.py:52`: separate token-classification regex, plus its ignored bytecode cache.
- `scripts/prewindow_check.sh:149`: bench `ps|grep`.
- `docs/process/NIGHT_HANDBACK.md:322`: preserved historical evidence.
- `docs/process/automation_history_2026-09-16.md:25,158,437`: dated historical account.

The installer’s separate label/plan census is untouched. Consult record 03 was absent from this checkout; implementation followed the adopted design supplied in the prompt.

## Residual risk

`envelopes_attempted` counts appended envelope records, so interruption during the first envelope reports zero. A driver argument containing `/claude/versions/` still matches the agent regex. Both remain unchanged for lead triage.

Next: bench-run the native tests, review the scoped diff, then update every active census producer and regenerate the manifest, wrapper, digest, plan, and probe receipt before the next night.