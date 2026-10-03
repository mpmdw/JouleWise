```json
{
"schema":"claude-codex-report/v1","genre":"implementation","status":"findings","completion":"complete","summary":"R1 and R4-R7 implemented, R2/R3 retained, R8 documented; focused checks pass and full-suite failures are baseline-compared.",
"workspace":{"base_requested":"b317866d04b4b2af1eaf4522df6563d87e8bafe3","base_mode":"descendant","head_start":"b2393079cecb14dc85fdb59d586101dce1610734","head_end":"b2393079cecb14dc85fdb59d586101dce1610734","upstream_end":"b317866d04b4b2af1eaf4522df6563d87e8bafe3","branch":"feat/2026-10-02-g2a-night-integration"},
"pathspec":["docs/phase_2/window_runbook.md","docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md","joulewise/night_agent_install.py","scripts/gen_g2_phase_d.py","scripts/generate_g2a_probe_inputs.py","scripts/run_night.py","scripts/summarize_g2a_prefill_probe.py","scripts/test_timings.json","tests/fixtures/custody_read_replay_allowlist.json","tests/test_generate_g2a_probe_inputs.py","tests/test_run_campaign.py","tests/test_run_night.py","scripts/harvest_g2a_window.py","tests/test_gen_g2a_window.py","tests/test_harvest_g2a_window.py"],
"unowned_dirty":[],
"verdict":{"implementation":"implemented","acceptance":"pending_verification"},
"verification":[
{"id":"V1","kind":"suite","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_gen_g2_phase_d tests.test_gen_g2a_window tests.test_generate_g2a_probe_inputs tests.test_summarize_g2a_prefill_probe tests.test_select_g2a_prefill_length tests.test_harvest_window tests.test_harvest_g2a_window tests.test_gen_derivation_night tests.test_check_window_provenance tests.test_run_campaign.G2aLowCountCampaignTests tests.test_custody_mode_inventory tests.test_shard_tests","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 225 tests in 120.039s","","OK","PASS built G2-a prompt ladder, configs, and manifests","PASS bound G2-a inputs to the calibration window"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V2","kind":"suite","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_run_night tests.test_run_night_probe_cadence tests.test_run_night_probe_worker_cadence tests.test_night_agent_install tests.test_night_gate","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 450 tests in 776.216s","","FAILED (failures=8, skipped=9)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V3","kind":"suite","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B scripts/shard_tests.py --workers 6 --split","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["WORKERS SUMMARY shards=6 modules=281 tests=7448 failures=64 errors=0 skipped=65 failed_shards=1,2,3,4,5,6 result=FAIL"]},"expected":{"exit_code":0,"tail_regex":"WORKERS SUMMARY .*failures=0 errors=0 .*result=PASS"}},
{"id":"V4","kind":"suite","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest discover -s tests","cwd":".","observed":{"result":"fail","exit_code":130,"tail":["KeyboardInterrupt"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V5","kind":"inspection","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/g2a-r2-baseline-proof.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["PASS baseline failure IDs match: battery_fixture=46 other_sandbox_identity=14 installer_boundary=2 process_cleanup=1; discovery_modules=277; no new IDs"]},"expected":{"exit_code":0,"tail_regex":"^PASS baseline failure IDs match:.*no new IDs$"}},
{"id":"V6","kind":"inspection","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B scripts/gen_g2_phase_d.py --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["PASS generated Phase D matches pinned runbook bytes"]},"expected":{"exit_code":0,"tail_regex":"^PASS generated Phase D matches pinned runbook bytes$"}},
{"id":"V7","kind":"smoke","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B scripts/gen_g2_phase_d.py --new-g2a-window /tmp/g2a-lane/final/night/night_plan.json --t0-epoch-s 1791003060 --window-max-s 34456 --plan-id g2a-final-desk-20261003 --measurement-root /Users/edr/night-custody/measurement/JouleWise-measurement-20261001T2252Z-r6-c2 --measurement-head 47e16dcc9492af707b477de32318f3192f41f888 --night-root /tmp/g2a-lane/final/night --g2a-root /tmp/g2a-lane/final/g2a","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["plan=/private/tmp/g2a-lane/final/night/night_plan.json chain=/private/tmp/g2a-lane/final/night/chain.zsh sha256=/private/tmp/g2a-lane/final/night/chain.zsh.sha256"]},"expected":{"exit_code":0,"tail_regex":"^plan=.* chain=.* sha256=.*$"}},
{"id":"V8","kind":"lint","cmd":"/bin/zsh -n /tmp/g2a-lane/final/night/chain.zsh","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},
{"id":"V9","kind":"smoke","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B scripts/run_night.py preflight --plan /tmp/g2a-lane/final/night/night_plan.json","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["{\"preflight\": \"ok\", \"python\": \"/Users/edr/code/JouleWise/.venv/bin/python\", \"version\": \"3.13.1\", \"modules\": [\"scripts.run_night\", \"joulewise.arm_readiness\", \"joulewise.arm_readiness_evidence_t0\", \"joulewise.t0_rehearsal\", \"joulewise.night_gate\", \"joulewise.measurement_liveness\"]}"]},"expected":{"exit_code":0,"tail_regex":"\"preflight\": \"ok\""}},
{"id":"V10","kind":"smoke","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/g2a-r2-argv-proof.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["PASS argv-only exit=0 tree_identical=True terminal=--verify-only"]},"expected":{"exit_code":0,"tail_regex":"^PASS argv-only exit=0 tree_identical=True terminal=--verify-only$"}},
{"id":"V11","kind":"inspection","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/g2a-r2-scope-proof.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["PASS scope: 15 allowed paths; staged=0; HEAD unchanged; diff clean; harvester=248 lines"]},"expected":{"exit_code":0,"tail_regex":"^PASS scope: 15 allowed paths; staged=0; HEAD unchanged; diff clean; harvester=248 lines$"}}
],
"flags":[
{"id":"F1","kind":"lead_ruling","level":"nonblocking","text":"Applied the Revision 6 fixture-identity ruling; original Revision 6 assertion values remain and generic mirror tests were added.","needs":""},
{"id":"F2","kind":"lead_ruling","level":"nonblocking","text":"All changes remain in the working tree. No lane git add, commit, stash, checkout or reset was run; tests use disposable Git fixtures.","needs":"Lead reviews and commits the authorized diff."},
{"id":"F3","kind":"environment","level":"nonblocking","text":"Base b2393079 reproduces 46 child-Python battery fixture failures, 14 sandbox/machine-identity failures, 3 installer boundary failure events and 1 process-cleanup failure. No fixes applied to these classes.","needs":"Lead verifies the baseline environment before claiming a green canonical suite."},
{"id":"F4","kind":"verification_gap","level":"nonblocking","text":"Serial canonical discovery was interrupted (130) for the 100-minute budget; the repository six-worker sharder completed the same discovery coverage. Required focused modules completed.","needs":""},
{"id":"F5","kind":"residual_risk","level":"nonblocking","text":"All evidence is desk/fixture tooling evidence. Variable-work sizing uses declared conservative allowances; live timing and hardware gates remain PROVISIONAL.","needs":"Lead owns final review, measurement-clone preparation and live admission/harvest verification."}
]
}
```

## Change

Completed the authorized implementation within 76 minutes. No `NEEDS_SCOPE` or `NEEDS_RULING` remains.

The [admission driver](/Users/edr/code/JouleWise-g2a-lane/scripts/run_night.py:3078) (+43/−12 lines) identifies Revision 6 by the exact registration SHA. Generic calibration chains retain physical admission, use their literal programmed span, and write physical start-condition evidence.

The [generator](/Users/edr/code/JouleWise-g2a-lane/scripts/gen_g2_phase_d.py:28) (+195/−2) adds code-based sizing, reservation inspection branches, typed refusal coordinates, and one-command v2 plan authoring. The [installer](/Users/edr/code/JouleWise-g2a-lane/joulewise/night_agent_install.py:785) (+25/−7) accepts that G2-a inspection surface while preserving derivation checks.

The [248-line harvester](/Users/edr/code/JouleWise-g2a-lane/scripts/harvest_g2a_window.py:1) verifies the archive before authentication, validates roster and members, assesses brackets, regenerates summaries, reports clocks, selects or recovers, and advances custody through governed procedures. [Producer replay](/Users/edr/code/JouleWise-g2a-lane/scripts/generate_g2a_probe_inputs.py:1236) (+63/−3) authenticates the frozen ledger prefix through the existing enforcing seam. [Summary support](/Users/edr/code/JouleWise-g2a-lane/scripts/summarize_g2a_prefill_probe.py:369) (+37/−1) filters strict-invalid members and reports capture clocks.

The [runbook recipe](/Users/edr/code/JouleWise-g2a-lane/docs/phase_2/window_runbook.md:2292) adds 76 lines; the [runsheet handoff](/Users/edr/code/JouleWise-g2a-lane/docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:1859) adds 16. Tests add 686/remove 9 lines, including the custody replay inventory; three timing-map lines record the new modules.

| Ruling | Evidence |
|---|---|
| R1 | `test_generic_calibration_uses_literal_budget_without_manifest`, `test_generic_missing_span_refuses_before_OFF`; existing Revision 6 manifest, settle, and 7680-second assertions retained. |
| R2 | Retained `test_stale_76_row_ledger_refuses_against_current_acceptance`, `test_any_ledger_snapshot_refusal_is_fatal`. |
| R3 | Retained `test_screen_check_detects_stale_source_and_rendered_literals`, `test_emission_derives_screen_even_from_stale_source`; generator check passes. |
| R4 | `test_argv_only_precedes_all_mutation_and_describes_actual_reservation`, `test_installer_render_only_succeeds_without_running_reservation`, `test_derivation_wrapper_without_source_still_refuses`. |
| R5 | `test_typed_calibration_refusal_path_is_night_custody`. |
| R6 | `test_one_command_authors_v2_plan_chain_sidecar_and_schedule`, `test_authoring_fences_refuse_before_publication`. |
| R7 | `test_complete_window_selects_archives_every_byte_and_advances_via_governed_procedure`, recovery/authentication/clock tests, and `test_unresolvable_prefill_is_strict_valid_and_does_not_spend_failure_budget`. Low-count summary and registered selector fallback are covered. |
| R8 | Retained C2 376-row seed documented in the recipe; stale 76-row refusal remains covered by R2. |

Every changed existing fixture is in `tests/test_run_night.py`: `make_probe_fixture`, `NightDriverTests.setUp`, `_run_calibration_stub`, `test_real_abort_command_refusal_reaches_the_driver_as_refused`, `_run_with_clean_dwell`, and `test_standard_plan_budget_preserves_programmed_span_and_gate_cost`. The latter two now use the actual Revision 6 registration bytes for Revision 6 expectations; generic fixtures carry their required literal span.

The final literal is **`NIGHT_PROGRAMMED_SPAN_S=33556`**, with minimum window **34456 seconds**. Its adjacent comment shows:

- Fixed work: `9×600 + 8×20 + 24×(75+5+1) + 2×196.703125 + 2×(20+5) = 7947.40625`.
- Small member: `60+30+30+52+300+30+48+30+120+153+48 = 901`.
- Large member: `120+60+60+103+300+30+48+30+120+153+48 = 1072`.
- Eight stages: `8×(120+60)=1440`; shared custody/authentication/summary: `1440`; calibration overhead: `420`.
- Total: `ceil(7947.40625 + 20×901 + 4×1072 + 1440 + 1440 + 420) = 33556`.

Sizing reads prospective code, policy, and panel constants. Unbounded work uses declared conservative allowances; archived measurements supplied no sizing values.

## Verification notes

Baseline controls used the round-2 starting commit `b2393079`. The affected environment-test and driver code is unchanged from requested base `b317866d`.

The 64 full-suite failure events comprise 46 battery-fixture failures, 14 machine/sandbox identity failures, three installer-boundary events across two methods, and one process-cleanup failure. All 63 failing method IDs match base. The suite also emitted an ignored Metal-device atexit warning.

Serial discovery was interrupted to respect the budget. The completed sharded run covered all 277 discovered modules; its 281 module executions include split-module repetitions. Full logs are [available here](/tmp/g2a-r2-canonical-final.log).

The recorded authoring command is a historical desk check with one-shot output paths. A live plan needs fresh coordinates and t0.

## Residual risk

Hardware and timing validation remain **PROVISIONAL**. The selected measurement clone must contain the reviewed implementation before live inspection.

Next exact step: lead reviews and commits the unstaged diff, prepares the measurement clone with the retained C2 seed, authors a fresh plan, and owns final live admission and harvest verification.