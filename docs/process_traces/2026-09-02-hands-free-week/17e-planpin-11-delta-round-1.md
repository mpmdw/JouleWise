# Delta re-audit of fix round 1 at bb5441e3 (terra xhigh, direct run), verbatim

```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"All requested cures bite under temp-copy reversion, but the installer heredoc trims a trailing LF from measurement_head and can arm a plan the driver will reject.","workspace":{"base_requested":"12ec41d2","base_mode":"exact","head_start":"bb5441e3205d77f5d1d86d2941bbca839f582431","head_end":"bb5441e3205d77f5d1d86d2941bbca839f582431","upstream_end":"bb5441e3205d77f5d1d86d2941bbca839f582431","branch":"feat/2026-09-03-night-plan-pin"},"pathspec":[],"unowned_dirty":[],"verdict":{"decision":"NOT LANDABLE","scope":"cold gate","findings":[{"id":"B2","severity":"blocker","site":"scripts/install_night_agent.sh:44-68,77-80","evidence":"A full v2 plan whose measurement_head is 40 lowercase hex plus a trailing LF installs with rc=0; scripts.run_night._load_plan rejects that same file as night_plan_malformed."}]},"verification":[{"id":"V1","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night tests.test_night_gate tests.test_install_night_agent","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 109 tests in 10.763s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 109 tests in .*\\n\\nOK"}},{"id":"V2","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_night_gate.NightGateTests.test_window_refusal_performs_no_command_or_file_or_head_probe tests.test_night_gate.NightGateTests.test_plan_age_refusals_precede_head_probes tests.test_night_gate.NightGateTests.test_driver_checkout_head_movement_is_informational_and_census_still_runs","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 3 tests in 0.000s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 3 tests in .*\\n\\nOK"}},{"id":"V3","kind":"smoke","cmd":"install full v2 plan with measurement_head=<40hex>+LF; assert rc=3","cwd":"$TMPDIR isolated copy","observed":{"result":"fail","exit_code":1,"tail":["FAIL expected installer rc=3 for trailing-LF measurement_head; actual rc=0 message="]},"expected":{"exit_code":3,"tail_regex":"measurement_head.*40 lowercase hex"}}],"flags":[{"id":"F1","kind":"residual_risk","level":"blocking","text":"Repair B2 and add a trailing-whitespace v2-field installer regression before landing.","needs":"Lead-directed fix and delta re-audit."}]}
```

## Findings

| ID | Severity | Site | Evidence |
|---|---|---|---|
| B2 | blocker | `scripts/install_night_agent.sh:44-68,77-80` | `plan_fields=("${(@f)$(...))` removes final newlines. A full v2 plan with `measurement_head="<40hex>\n"` installed: `rc=0`, empty message. The same file through `_load_plan` returned `night_plan_malformed: measurement_head must be exactly 40 lowercase hexadecimal characters`. It arms a night guaranteed to refuse. Validate raw Python values before emitting shell fields, and add this regression. |

| Finding | Cure closes? | Temp-copy reversion result / failing test |
|---|---|---|
| B1 | Yes | Move probes above age checks → `NightGateTests.test_plan_age_refusals_precede_head_probes` failed twice: expected `night_plan_stale` / `night_plan_malformed`, got `night_probe_error`. |
| S1 | Yes | Use `str(REPO_ROOT)` instead of `root` → `NightDriverTests.test_matching_real_measurement_checkout_uses_requested_root_and_strips_head` failed at the pinned-HEAD equality. |
| S2 | Yes | Remove measurement-probe `.strip()` → same named test failed: returned head differed only by trailing `\n`. |
| L1 root | Yes | Delete absolute-root guard → `InstallNightAgentTests.test_install_refuses_relative_measurement_root` failed: expected `measurement_root`, got measurement-head mismatch. |
| L1 head | No—B2 | Delete hex guard → `InstallNightAgentTests.test_install_refuses_measurement_head_that_is_not_40_lowercase_hex` failed for uppercase and 39-hex inputs. The current guard misses a trailing LF because heredoc transport normalizes it. |
| L2 | Yes | Restore direct `data[...]` fields → `InstallNightAgentTests.test_v1_install_is_retired_without_traceback_but_uninstall_still_works` failed (`expected rc 3`, got `1`). |
| N1 | Yes | Revert the doc hunk → named cure check, handback-mechanism inspection, exited 1 on legacy installer/gate wording. No unit test exists; the cure table specifies diff inspection. |

| Ordered-gate execution | Observed |
|---|---|
| Expired window | `window reason=night_window_expired probes=0` |
| Aged plan + failing measurement probe | `aged failing-probe reason=night_plan_stale head_probes=0` |
| Census path C5 fields | `verdict=REFUSED census_called=True`; C5 retained plan/driver/plan-measurement/measurement-checkout heads: `aaaa…`, `bbbb…`, `aaaa…`, `aaaa…`. |

| Installer heredoc input | Exit / message |
|---|---|
| v1 | `rc=3` — `plan schema joulewise.night_plan.v1 is retired; re-author under joulewise.night_plan.v2 (missing measurement_root/measurement_head)` |
| v2 relative root | `rc=3` — `plan measurement_root must be an absolute path: .` |
| uppercase head | `rc=3` — `plan measurement_head is not 40 lowercase hex: A…A` |
| 39-hex head | `rc=3` — `plan measurement_head is not 40 lowercase hex: a…a` |
| valid v2 | `rc=0` — empty message |

`git diff -U0 12ec41d2 -- docs/process/NIGHT_HANDBACK.md` has one hunk at line 63: only the obsolete pin/uninstall and dev-checkout mechanism sentences changed. The replacement matches code: install compares both pins (`:81-95`), uninstall bypasses them (`:43`), and the gate compares measurement HEAD after age checks (`night_gate.py:619-645`) while retaining driver HEAD only as C5 evidence.

Verdict: **NOT LANDABLE** for the cold gate.

## Residual risk

No live launchd/courier or hardware run was performed; all execution used isolated `$TMPDIR` copies.