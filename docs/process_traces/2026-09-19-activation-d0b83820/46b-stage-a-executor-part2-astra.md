```json
{
  "schema":"claude-codex-report/v1",
  "genre":"implementation",
  "status":"blocked",
  "completion":"partial",
  "summary":"Stage A executor units implemented; automatic upper-confidence sizing needs R3; baseline/environment verification remains red.",
  "workspace":{"base_requested":"3e4acc59","base_mode":"exact","head_start":"3e4acc59b2bdcd28844fdad31418bdca05db037d","head_end":"3e4acc59b2bdcd28844fdad31418bdca05db037d","upstream_end":"3e4acc59b2bdcd28844fdad31418bdca05db037d","branch":"feat/2026-09-19-stage-a-evidence-executor"},
  "pathspec":["configs/campaigns/quiet_predicate_evidence_01/README.md","configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v1.json","docs/phase_2/derivation_night_runbook.md","docs/process/NIGHT_COURIER_PROMPT.md","docs/process/NIGHT_HANDBACK.md","joulewise/night_agent_install.py","joulewise/night_gate.py","joulewise/quiet_predicate_campaign.py","scripts/gen_evidence_night.py","scripts/night_chains/quiet_predicate_evidence.zsh","scripts/run_night.py","scripts/sample_quiet_predicate_evidence.py","tests/test_gen_evidence_night.py","tests/test_night_agent_install.py","tests/test_night_gate.py","tests/test_quiet_predicate_campaign.py","tests/test_run_night.py","tests/test_sample_quiet_predicate_evidence.py"],
  "unowned_dirty":[],
  "verdict":{"implementation":"partial","acceptance":"needs_ruling"},
  "verification":[
    {"id":"V1","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_night_gate -q","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 70 tests in 0.570s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V2","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_gen_evidence_night -q","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 5 tests in 1.043s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V3","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_quiet_predicate_campaign -q","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 8 tests in 0.270s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V4","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_sample_quiet_predicate_evidence -q","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 54 tests in 7.888s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V5","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_run_night.EvidenceProbeTests tests.test_run_night.EvidenceProbeFailureTests tests.test_run_night.CalibrationProbeByteCompatibilityTests tests.test_night_agent_install.EvidenceProbeReceiptTests tests.test_quiet_predicate_campaign tests.test_gen_evidence_night -q","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 25 tests in 12.134s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V6","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_run_night -v","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 190 tests in 133.818s","FAILED (failures=1, skipped=9)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V7","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_night_agent_install -v","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 60 tests in 919.865s","FAILED (failures=1)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V8","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B scripts/quick_suite.py --tier quick --workers 4","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 7 tests in 0.999s","FAILED (failures=2)","QUICK SUMMARY tier=quick modules=153 excluded=88 failures=1 seconds=102.628 result=FAIL"]},"expected":{"exit_code":0,"tail_regex":"QUICK SUMMARY.*failures=0.*result=PASS"}},
    {"id":"V9","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/stagea_verify_baseline.py","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 2 tests in 8.368s","FAILED (failures=2)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V10","kind":"inspection","cmd":"python3 /tmp/stagea_scope_check.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[" 11 files changed, 806 insertions(+), 24 deletions(-)","SCOPE_OK: 18 authorized paths; no out-of-scope changes","SYNTAX_OK: changed Python and evidence zsh"]},"expected":{"exit_code":0,"tail_regex":"(?s)SCOPE_OK: 18 authorized paths.*SYNTAX_OK"}},
    {"id":"V11","kind":"inspection","cmd":"launchctl list","cwd":".","observed":{"result":"fail","exit_code":1,"tail":[]},"expected":{"exit_code":0,"tail_regex":".*"}}
  ],
  "flags":[
    {"id":"R3","kind":"lead_ruling","level":"blocking","text":"The ruling specifies an upper 90% bound on adjacent-pair SD but does not settle the confidence construction for overlapping differences or exclusions. s_upper and automatic block-two sizing remain unset.","needs":"Rule the estimator, dependence assumptions, effective degrees of freedom and exclusion handling; resume that bounded reducer unit."},
    {"id":"F1","kind":"environment","level":"nonblocking","text":"Quick tier fails test_axi_controller_events on unavailable process identity; /bin/ps is denied and pgrep cannot obtain the process list. Installer census failure reproduces on untouched 3e4acc59.","needs":"Replay required checks in the lead bench environment."},
    {"id":"F2","kind":"verification_gap","level":"nonblocking","text":"Driver journal_block watchdog timeout also reproduces on untouched 3e4acc59; its cause was not established here. Full discovery was not run because it includes canonical-root consumers excluded by the seat runner.","needs":"Lead owns baseline timeout diagnosis and final full replay."},
    {"id":"F3","kind":"verification_gap","level":"nonblocking","text":"No real LaunchAgent install or live power capture was invoked. launchctl list returned 1 without output; the requested grep remained empty, so absence of loaded jobs is not proven. Cleanup tests are fixtures, not hardware evidence.","needs":"Lead verifies launchd inventory and live cleanup before any arm."}
  ]
}
```

## Change

Implemented the registration gate, sealed authoring tool, evidence chain, typed probe receipt, driver inventory/cleanup integration, remaining harness joins and interior reduction, and documentation amendments. The calibration probe receipt matches part-1 bytes in the regression fixture.

The pilot records spread and preserves exclusions. Automatic `s_upper` calculation and its downstream sizing remain blocked on R3. No workspace commit, push, real installation, or power capture was performed.

**CLAUSE MAP** — paths below are repository-relative; test references identify the biting regression.

| Ruled proposition | Implementation | Biting test | Counterfactual caught |
|---|---|---|---|
| 10a Q1: digest-keyed registrations and honest C1 metadata | `joulewise/night_gate.py:49`, `:1386` | `tests/test_night_gate.py:1280`, `:1298` | Evidence borrows D-166, calibration borrows the pilot, or C1 reports the wrong registration. |
| 46a R1: measure tracked source against wrapper literal | `joulewise/night_gate.py:1177` | `tests/test_night_gate.py:1291` | Changed source passes through an advisory sidecar. |
| 46a R2: additive admission metadata; unchanged calibration probe | `joulewise/night_gate.py:1428`, `scripts/run_night.py:3348` | `tests/test_night_gate.py:1190`, `tests/test_run_night.py:4786` | Existing admission values or calibration probe bytes change. |
| 10a Q2: frozen 600-second settle, twelve envelopes, 480-second interiors, no load | `pilot_protocol_v1.json:1` under the campaign directory; `joulewise/quiet_predicate_campaign.py:317` | `tests/test_quiet_predicate_campaign.py:112` | Wrong count, timing, recorder count, or a load invocation. |
| 10a Q2: named exclusions; busy cores remain covariates; no top-up | `joulewise/quiet_predicate_campaign.py:204`, `:254` | `tests/test_quiet_predicate_campaign.py:37`, `:55` | High busy cores exclude observations, or exclusions bridge nonadjacent envelopes. |
| 10a Q2: upper-bound sizing, floor three, three stop branches | `joulewise/quiet_predicate_campaign.py:230`, `:237`, `:302` | `tests/test_quiet_predicate_campaign.py:24`, `:49` | Point-SD sizing substitutes for the upper bound, or a stop condition qualifies a cutoff. **Confidence construction remains R3.** |
| 10a Q3: sealed manifest and authoring refusals | `scripts/gen_evidence_night.py:19`; `joulewise/quiet_predicate_campaign.py:51` | `tests/test_gen_evidence_night.py:69`, `:83`, `:92`, `:104` | Overrides, v4/non-diagnostic plans, calibration chains, or dirty tracked inputs produce a wrapper. |
| 10a Q3: shared literal dispatch; typed receipt; freshness and digest checks | `joulewise/night_gate.py:68`; `joulewise/night_agent_install.py:794`, `:888`, `:917`; `scripts/run_night.py:3357` | `tests/test_night_agent_install.py:1906`, `:1923`, `:1934`, `:1947` | Ambiguous payloads, stale receipts, custody fields, or substituted bindings pass. |
| 10a Q3: verify-only starts no collection or load | `scripts/night_chains/quiet_predicate_evidence.zsh:11`; `scripts/run_night.py:3311` | `tests/test_run_night.py:4698`, `:4734`, `:4748`, `:4814` | Missing/duplicate markers, timeout, chain failure, or changed inputs produce success. |
| Consult 44 F1: inventory and cleanup before courier | `scripts/run_night.py:961`, `:1238`; `joulewise/quiet_predicate_campaign.py:144` | `tests/test_run_night.py:4759`, `:4771`; `tests/test_quiet_predicate_campaign.py:80` | Envelope artifacts disappear or residue permits courier launch. |
| Consult 44 F2: preserve part-1 build and hard-probe evidence | `scripts/sample_quiet_predicate_evidence.py:695`, `:791` | `tests/test_sample_quiet_predicate_evidence.py:284`, `:339`, `:911` | Probe failures disappear or substituted session/build identities qualify. |
| Consult 44 F2: worker identity and monotonic load support | `scripts/sample_quiet_predicate_evidence.py:313` | `tests/test_sample_quiet_predicate_evidence.py:1125`, `:1131`, `:1149` | PID reuse, wrong boot, calibration periods, missing support, or failed cleanup count as delivered load. |
| Consult 44 F2: native interior integration and retained partial evidence | `scripts/sample_quiet_predicate_evidence.py:296` | `tests/test_sample_quiet_predicate_evidence.py:1100` | A scaled whole-envelope mean or partial coverage masquerades as a complete interior integral. |
| 10a Q3: handback/runbook amendments and descriptive courier | `docs/process/NIGHT_HANDBACK.md:88`, `:136`, `:571`; `docs/phase_2/derivation_night_runbook.md:3049`; `docs/process/NIGHT_COURIER_PROMPT.md:46` | `tests/test_night_gate.py:1324` | Required contract clauses or the courier’s authority boundary disappear. |

## Verification notes

The quick-tier failure is `test_axi_controller_events`: process identity is unavailable because `/bin/ps` is denied.

The installer’s census-related failure and driver’s eight-second `journal_block` timeout both reproduce in an untouched `3e4acc59` scratch archive. The watchdog timeout’s underlying cause remains unresolved. Later-added regressions were run separately in the focused checks.

Full discovery was not run because it includes canonical-root consumers excluded by the seat runner. The scoped diff stat covers eleven tracked files; seven new files are also listed in `pathspec`.

The initial and final `launchctl list | grep joulewise.night` checks were both empty. Since `launchctl list` itself returned 1, that does not prove inventory absence.

## Residual risk

**NEEDS_RULING R3:** Which upper-90% confidence construction, dependence assumptions, and effective degrees of freedom apply to the eleven overlapping adjacent differences—and to retained patterns after exclusions?

Options considered: a dependence-aware construction preserving the ruled adjacent differences, or an explicit protocol amendment using disjoint pairs. Recommend the former, with exclusion handling frozen explicitly. Treating overlapping differences as independent would introduce an unruled statistical assumption.

**Blocked work:** compute `s_upper`, automatically derive block-two `n`, and apply the resulting size-based stop decision in the pilot summary. The formula and stop helpers are implemented; the summary leaves these derived values unset.

**Next exact step:** lead rules R3, then resumes that reducer unit before independent review and final bench verification. Live cleanup remains unverified.