```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"clean","completion":"complete","summary":"B1 complete under 30a; 162 tests pass.","workspace":{"base_requested":"7c377d72","base_mode":"exact","head_start":"7c377d72","head_end":"7c377d72","upstream_end":"1b3992a3","branch":"feat/2026-09-20-evidence-night-lifecycle"},"pathspec":["joulewise/evidence_night.py","tests/test_evidence_night.py","docs/contracts/evidence_night_entry.md"],"unowned_dirty":[],"verdict":{"implementation":"implemented","acceptance":"ready"},"verification":[{"id":"V1","kind":"inspection","cmd":"git diff --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}],"flags":[]}
```

## Change

Retained the held B1 implementation and completed T3 under ruling 30a. Verification requires both labels typed LOADED, matching installed-plist fields, and exact equality with sealed render bytes. JSON evidence includes liveness, plist paths and both SHA-256s. No launchctl calendar parsing.

Tests cover field drift, extra plist keys, equivalent values serialized into different bytes, and ABSENT/UNKNOWN outcomes for **both labels**.

In the table, `L` means `tests.test_evidence_night.LifecycleTests`; `C` means `tests.test_evidence_night.LifecycleCompositionTests.test_prepare_check_real_installer_fake_launchctl_verify_and_uninstall`.

| Command | Coverage → tests |
|---|---|
| `check` | Seals and sole permitted write → `L.test_sealed_bytes_checked_before_host_probes`, `L.test_check_passes_and_writes_only_check_json`. Canonical ancestry/cleanliness and required fix → `L.test_canonical_must_contain_h_and_be_clean`, `L.test_candidate_must_contain_census_fix`. Supervisor arrival, rewind/re-add, missing reflog and process identity → `L.test_supervisor_uses_oldest_continuous_entry_not_latest`, `L.test_supervisor_rewind_readd_and_missing_reflog_fail_closed`, `L.test_supervisor_pid_reuse_absence_and_observation_errors`. Courier → `L.test_courier_unavailable`. Discovery → `L.test_discovery_retains_every_harvested_root_and_refuses_unknown`. Census/observation failures → `L.test_census_foreign_workload_and_unknown_refuse`, `L.test_raw_census_failure_and_missing_supervisor_state_refuse`. Retry routing → `L.test_retry_routes_exact_causes_and_unknown_stops`. Prepare + check never invoke launchctl → `C`. |
| `publish-install` | Preconditions → `L.test_publish_requires_check_armable_freshness_notice_and_sealed_bytes`. Atomic publication and real installer/probe through fake launchctl → `C`. Recovery ordering and byte preservation → `L.test_post_publication_failure_uninstalls_before_matching_byte_restore`, `L.test_nonzero_cleanup_or_changed_bytes_preserves_published_state`. Verification failure/defect recovery → `L.test_verify_failure_and_unexpected_defect_both_recover`. Interrupted publication → `L.test_exception_immediately_after_atomic_move_still_uninstalls`. Existing publication/cross-device refusal → `L.test_existing_publication_and_cross_device_refuse_without_installer`. |
| `verify` | `C`: both labels; plan-derived calendars and boundaries; label, argv, interpreter, plan path, root and RunAtLoad drift; exact render-byte equality; LOADED/ABSENT/UNKNOWN. Fake print output contains no calendar text. |
| `uninstall` | Nonzero recorded and immediate stop → `L.test_uninstall_records_nonzero_and_does_nothing_else`. Successful real installer cleanup, both fake jobs absent, published plan preserved → `C`. |

All four CLI success/refusal/defect exit paths: `L.test_cli_success_refusal_and_defect_split`.

Executed once from the worktree:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v tests.test_evidence_night tests.test_evidence_arm_sequence tests.test_install_night_agent tests.test_arm_census tests.test_arm_retry > /tmp/evidence-night-b1-30a-verification.log 2>&1
```

Counts respectively: **44 / 1 / 65 / 20 / 32**. Exit **0**. Exact tail:

```text
----------------------------------------------------------------------
Ran 162 tests in 278.683s

OK
```

## Verification notes

Used the authorized five-module fallback; canonical discovery was not run. Record 26’s previous full replay took approximately 59 minutes. Full output: [verification log](/tmp/evidence-night-b1-30a-verification.log).

HEAD remained `7c377d72`. The shared `origin/main` reference advanced from `ccfada60` to `1b3992a3` during verification; no fetch or Git mutation was performed by this session. Only the three allowed files are dirty. No commits.

## Residual risk

Evidence remains **PROVISIONAL**, using fixture repositories, injected census, fake launchctl and a synthetic probe receipt. No real launchctl, mail, network, courier execution or measurement was performed.

Notice transport, notice reading/veto integration, full `retry_allowed` clearance and courier execution remain deferred to B2/the bench. Courier availability is checked; the supplied notice ID is recorded verbatim and remains unverified. Handbook/runbook replacement and bookkeeping remain lead-owned.

No outstanding NEEDS_RULING or scope request. Next step: lead diff review and final verification.