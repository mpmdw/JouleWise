```json
{
"schema":"claude-codex-report/v1","genre":"implementation","status":"blocked","completion":"partial",
"summary":"Evidence execution and courier defects fixed; S4 ruling-path guard needs lead-owned records outside WRITE_SCOPE.",
"workspace":{"base_requested":"087bf3afc9f46e11edce9ab0376b0a8f7e2762df","base_mode":"exact","head_start":"087bf3afc9f46e11edce9ab0376b0a8f7e2762df","head_end":"087bf3afc9f46e11edce9ab0376b0a8f7e2762df","upstream_end":"6032b9e93220f9c9b9a04ca6d1dc75aa4aa92942","branch":null},
"pathspec":["configs/campaigns/quiet_predicate_evidence_01/README.md","configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v1.json","docs/process/NIGHT_HANDBACK.md","joulewise/night_gate.py","joulewise/quiet_predicate_campaign.py","scripts/gen_evidence_night.py","scripts/run_night.py","scripts/sample_quiet_predicate_evidence.py","tests/test_gen_evidence_night.py","tests/test_night_gate.py","tests/test_quiet_predicate_campaign.py","tests/test_run_night.py","tests/test_sample_quiet_predicate_evidence.py"],
"unowned_dirty":[],
"verdict":{"implementation":"partial","acceptance":"needs_ruling"},
"verification":[
{"id":"V1","kind":"test","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_quiet_predicate_campaign -q","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 22 tests in 0.563s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V2","kind":"test","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_night_gate -q","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 72 tests in 0.584s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V3","kind":"test","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_gen_evidence_night -q","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 7 tests in 2.276s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V4","kind":"test","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_sample_quiet_predicate_evidence -q","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 57 tests in 10.740s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V5","kind":"test","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_run_night -q","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 197 tests in 147.577s","FAILED (failures=1, skipped=9)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V6","kind":"test","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_quiet_predicate_campaign tests.test_gen_evidence_night tests.test_sample_quiet_predicate_evidence tests.test_night_gate.EvidenceRegistrationTests tests.test_run_night.EvidenceProbeTests tests.test_run_night.EvidenceProbeFailureTests tests.test_run_night.CalibrationProbeByteCompatibilityTests tests.test_night_agent_install.EvidenceProbeReceiptTests -q","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 111 tests in 27.454s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V7","kind":"suite","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_night_gate tests.test_gen_evidence_night tests.test_quiet_predicate_campaign tests.test_sample_quiet_predicate_evidence tests.test_run_night tests.test_night_agent_install tests.test_gen_derivation_night -q","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 460 tests in 1117.641s","FAILED (failures=3, skipped=9)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V8","kind":"suite","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B scripts/quick_suite.py --tier quick --workers 4","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["QUICK SUMMARY tier=quick modules=153 excluded=88 failures=1 seconds=116.267 result=FAIL"]},"expected":{"exit_code":0,"tail_regex":"result=PASS"}},
{"id":"V9","kind":"test","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/stagea-fix-negative-oracles.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["NEGATIVE_ORACLES_PASS: B1 B2 S1(all five) S2 S3 56c-R2 56x-R2"]},"expected":{"exit_code":0,"tail_regex":"NEGATIVE_ORACLES_PASS"}},
{"id":"V10","kind":"test","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/stagea-fix-courier-oracles.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["56c-R1 fixed=PASS mutant=FAIL FAILED (failures=2)","56x-R1 fixed=PASS mutant=FAIL FAILED (failures=1)","COURIER_ORACLES_PASS"]},"expected":{"exit_code":0,"tail_regex":"COURIER_ORACLES_PASS"}},
{"id":"V13","kind":"suite","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest discover -s tests > /tmp/stagea-fix-canonical.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":130,"tail":["KeyboardInterrupt"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V14","kind":"inspection","cmd":"git diff --check && git diff --stat","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[" 13 files changed, 563 insertions(+), 133 deletions(-)"]},"expected":{"exit_code":0,"tail_regex":"13 files changed"}}
],
"flags":[
{"id":"F1","kind":"scope_deviation","level":"blocking","text":"NEEDS_SCOPE: S4 serialized-table pin is implemented, but the QPE authority records are absent here. No out-of-scope writes were made.","needs":"Lead imports the listed records or prospectively expands scope; resume to attach ruling paths and enforce existence."},
{"id":"F2","kind":"environment","level":"nonblocking","text":"Host ps/pgrep census is blocked. Journal timeout, installer census failure and quick-tier failures reproduce at base. Combined-run startup timeout passes isolated base/fix checks.","needs":"Lead replays host process/courier cleanup checks outside this sandbox. Fixture evidence remains PROVISIONAL."},
{"id":"F3","kind":"verification_gap","level":"nonblocking","text":"Extra canonical discovery was interrupted with exit 130 at the scope-blocked partial handback; it has no complete result. No live collection, install, commit or reverse bridge hop occurred.","needs":"Lead performs final canonical replay after S4 is completed."}
],
"scope_expansion":{"requested_paths":["docs/process_traces/2026-09-19-activation-d0b83820/10-coldgate-packet-stage-a-executor/10-coldgate-fable-ruling.md","docs/process_traces/2026-09-19-activation-d0b83820/46b-ruling-stage-a-seat-r3.md","docs/process_traces/2026-09-19-activation-d0b83820/61a-triage-opus-counter-review-stage-a.md"],"reason":"S4 requires registration.ruling to name existing repository record paths; these governing QPE records exist only in the supplied lead worktree.","blocked_work":"Complete S4 ruling-path metadata and existence regression.","minimal_change":"Import the three existing lead records verbatim, then finish the in-scope table metadata and test."}
}
```

## Change

Implemented the runtime fixes and defect regressions. S4 is partial: the serialized table pin rejects unruled amendments, but its record-existence guard requires the missing authority files.

In the clause map, `campaign`, `driver`, and `sampler` refer to `joulewise/quiet_predicate_campaign.py`, `scripts/run_night.py`, and `scripts/sample_quiet_predicate_evidence.py`.

| Finding | Site | Biting regression | Counterfactual |
|---|---|---|---|
| B1 | `campaign.execute`, `pilot_summary` | `test_envelope_three_collect_error_continues_frozen_cadence_retains_eleven`; `test_isolated_cleanup_unproven_continues_but_two_consecutive_refuse` | Restoring first-error abort fails. Isolated cleanup failures continue; two consecutive failures produce a refusal. |
| B2 | `campaign.main`, `process_groups`; generator refusal transport | `test_preexecute_manifest_mismatch_writes_typed_refusal_and_courier_runs`; `test_wrapper_source_mismatch_writes_typed_preexecute_refusal` | Restoring missing-journal failure breaks the real courier regression. |
| S1 | Protocol validation, sizing, stop evaluation, gate digest | `test_all_five_sizing_constants_are_read_from_frozen_protocol` | Five separate code-constant mutants each fail. |
| S2 | `campaign.cleanup_groups`; supervised recorder stop | `test_foreign_group_eperm_is_logged_absence_alone_proves_cleanup`; `test_power_supervised_stop_eperm_is_logged_and_finish_still_reaps` | Treating EPERM as fatal fails despite subsequent proven absence. |
| S3 | `campaign.pilot_summary` journal join | `test_recorder_excursion_joins_only_envelope_five_never_retention` | Removing the journal read fails the envelope-five assertion. |
| S4 — partial | Serialized registration-table pin | `test_ruled_registration_serialization_requires_dated_ruling_amendment` | An added unruled entry fails. Record-path existence remains scope-blocked. |
| 56c R1 | Receipt-only cleanup dispatch | `test_rehearsal_and_wrapper_missing_calibration_always_deliver`; `test_evidence_identity_dispatches_cleanup_without_reading_wrapper` | Restoring wrapper-based dispatch fails legacy delivery. |
| 56c R2 | Whole-round observer-cost stop input | `test_twelve_constant_energies_point_one_observer_core_stops` | Omitting `observer_floor` fails: 0.1 core must produce “no cutoff qualifies.” |
| 56x R1 | Shared `cleanup_record`; real courier | `test_successful_evidence_night_courier_reads_existing_executor_cleanup` | Restoring exclusive recreation suppresses delivery and fails. Existing bytes remain unchanged on repeated reads. |
| 56x R2 | Scheduled interior mapping; registered 10-second tolerance | `test_scheduled_interior_does_not_move_with_two_second_collector_start_drift`; `test_start_drift_ten_seconds_included_beyond_excluded_by_name` | Restoring actual-start anchoring fails the fake-clock test. |
| 62 N1 | Separate Darwin join ladder | `test_load_worker_runs_its_window_after_the_rendezvous` | Pipe-closure coverage remains in the cross-platform fake-clock test. |
| 61 N1–N4 | Imports, file-owned validation, diagnostic labels | Frozen-protocol and overlapping-pair regressions | Duplicate imports/value definitions removed; overlapping diagnostics explicitly labelled. Chain comment already said “timing.” |
| 61 N5 | Evidence-dispatch progress | `test_evidence_worker_crash_progress_keeps_typed_failure_schema` | A worker-entry crash retains evidence schema for the supervisor’s failure receipt. |
| 61 N6 | Gate source acquisition | `test_unavailable_chain_source_is_probe_error_not_digest_mismatch` | Unavailable source must report `night_probe_error`. |
| 61 N7 | Authenticated protocol reread | `test_protocol_reread_mutation_refuses_before_execute` | Mutation after manifest verification refuses before execution. |

## Verification notes

The broad failures were:

- `test_blocked_journal_never_blocks_deadline_or_grants_go`: reproduced at exact starting HEAD.
- `test_cleanup_refusal_reports_the_failure_it_interrupted`: reproduced at starting HEAD; process census is unavailable.
- `test_startup_hang_is_nonblocking`: timed out in the combined run; isolated baseline and fixed checks passed in 6.421 s and 6.600 s. Cause remains unresolved.
- Quick-tier AXI failures: both reproduced at starting HEAD.

Evidence is retained in [baseline results](/tmp/stagea-fix-baseline.log), [installer baseline](/tmp/stagea-fix-baseline-installer.log), and [startup recheck](/tmp/stagea-fix-startup-recheck.log).

Records 55/59 enumerate six distinct modules; I added `test_gen_derivation_night` as the seventh compatibility module. The extra canonical run was interrupted at the scope blocker; no full-suite pass is claimed.

B1 counts **12 attempts, one failed, 11 retained**, resolving the ruling’s inconsistent “11 attempted / one excluded / retained 11” wording. At this branch head, the Pipe-closure block was already cross-platform; the Darwin-only ladder is now separate.

## Residual risk

**NEEDS_SCOPE:** import the three records listed in `scope_expansion`, or prospectively expand the allowlist, then resume S4’s ruling-path metadata and existence test. Those files are outside the exhaustive `WRITE_SCOPE`; none was modified.

Final host cleanup verification and canonical replay remain lead-owned. Evidence remains **PROVISIONAL**.