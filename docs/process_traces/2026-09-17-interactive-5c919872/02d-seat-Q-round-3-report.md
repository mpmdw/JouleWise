```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented bind-supervision redesign; 341 tests pass and all 13 mutants fail as expected. Changes unstaged; no commits.",
  "workspace": {"base_requested":"5c5a3323","base_mode":"exact","head_start":"5c5a33235e4a98b87139c4567dc211cc68d7c527","head_end":"5c5a33235e4a98b87139c4567dc211cc68d7c527","upstream_end":"9eb1a0d15ba9c3289c60a49094fd195d442f8db4","branch":"feat/2026-09-17-night-gate-quiet-admission"},
  "pathspec": ["docs/contracts/night_quiet_admission.md","joulewise/night_gate.py","joulewise/quiet_admission.py","scripts/run_night.py","tests/test_quiet_admission.py","tests/test_run_night.py","tests/night_gate_fixtures/bind_supervision.py"],
  "unowned_dirty": [],
  "verdict": {"implementation":"implemented","acceptance":"pending_verification"},
  "verification": [{"id":"V1","kind":"suite","cmd":"TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_night_gate tests.test_quiet_admission tests.test_night_plan_writer tests.test_arm_retry tests.test_run_night tests.test_gen_derivation_night 2>&1 | tail -4","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["----------------------------------------------------------------------","Ran 341 tests in 69.093s","","OK (skipped=9)"]},"expected":{"exit_code":0,"tail_regex":"(?s)Ran 341 tests.*OK \\(skipped=9\\)"}},{"id":"V2","kind":"build","cmd":"PYTHONPYCACHEPREFIX=/tmp/jw-compile python3 -m compileall -q scripts joulewise; echo rc=$?","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["rc=0"]},"expected":{"exit_code":0,"tail_regex":"rc=0"}},{"id":"V3","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_derivation_night.py --check; echo rc=$?","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["PASS generated derivation-night wrapper region matches","rc=0"]},"expected":{"exit_code":0,"tail_regex":"(?s)PASS.*rc=0"}},{"id":"V4","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/jw-r3-mutants.py > /tmp/jw-r3-mutants-final.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},{"id":"V5","kind":"inspection","cmd":"git diff --stat\ngit status --short","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[" docs/contracts/night_quiet_admission.md |  75 ++-"," joulewise/night_gate.py                 |  10 +"," joulewise/quiet_admission.py            |  71 ++-"," scripts/run_night.py                    | 867 +++++++++++++++++++++++---------"," tests/test_quiet_admission.py           |  34 +-"," tests/test_run_night.py                 | 327 ++++++++----"," 6 files changed, 1044 insertions(+), 340 deletions(-)"," M docs/contracts/night_quiet_admission.md"," M joulewise/night_gate.py"," M joulewise/quiet_admission.py"," M scripts/run_night.py"," M tests/test_quiet_admission.py"," M tests/test_run_night.py","?? tests/night_gate_fixtures/bind_supervision.py"]},"expected":{"exit_code":0,"tail_regex":"(?s)6 files changed.*bind_supervision.py"}},{"id":"V6","kind":"test","cmd":"TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/jw-r3-profile.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["----------------------------------------------------------------------","Ran 18 tests in 15.782s","","OK","maximum_new_test_s=2.698 tests.test_run_night.BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go"]},"expected":{"exit_code":0,"tail_regex":"(?s)Ran 18 tests.*OK.*maximum_new_test_s=2\\."}}],
  "flags": [{"id":"F1","kind":"verification_gap","level":"nonblocking","text":"Native observer-cost smoke remains lead-owned, as directed; no live sampler or arming performed.","needs":"Run python3 -B -m joulewise.quiet_admission --sample-interval-s 30 natively; retain cold-gate merge review."}]
}
```

## Change

Changes are unstaged; no commits or early return. Reason codes and acquisition/courier/dead-man constants are unchanged.

1. Capped, nonblocking framed transport for every job: M2, M3, M7, M8 below.
2. One ticker services deadline, census, transport and cleanup. Regressions 1/2/5/8 pass; `test_stalled_census_does_not_suppress_later_census` also passes.
3. Immediate group cancellation and nonblocking reaping: M1, M5, M10.
4. Bounded journal queue, durable acknowledgements and incremental digest/count; receipt `journal_failure` prevents GO. Proven by M9, `test_journal_failure_and_saturation_are_terminal`, and `test_final_hard_checks_follow_delayed_journal_ack`.
5. Exec/private workers and full-observation CLI; the test hook never forks. Proven by `test_production_worker_argv_are_exact` and `ObservationWorkerCliTests`.
6. Interval + 215 s local allowance; local ERROR can recover, global expiry stays distinct: M4 and regression 10. Regression 8 now checks local ERRORs before expiry; its synthetic 270 s samples declare a 270 s interval.
7. Parent self/children rusage brackets worker startup through reaping and journal acknowledgement. Proven by `test_parent_measures_whole_round_cost` and the smoke CLI test.
8. Eighteen supervision tests; fault cases use acknowledged fault points, fake time and an external watchdog with production transport/cleanup.
9. All 13 mutants executed in `/tmp` copies and failed as expected.
10. Contract documents supervision, protocol, grace and failure codes; Terms remains the first section.

## Verification notes

Mutant tests below are `BindSupervisionProcessTests.test_<suffix>` unless qualified. Assertion excerpts are verbatim; watchdogs fired at 8 s. Replay: `/tmp/jw-r3-mutants.py`; logs and copies: `/tmp/jw-r3-mutant-evidence/`.

| Row | Test suffix | Executed mutant failure |
|---|---|---|
| M1: join, startup / published | `startup_hang_is_nonblocking`; `post_send_hang_is_consumed_once_and_reaped` | `external watchdog (8 s)` for both |
| M2: blocking receive | `header_plus_one_byte_never_blocks_recv` | `external watchdog (8 s)` |
| M3: partial EOF | `partial_header_and_body_eof_are_errors` | `'night_refused_bind_expired' != 'night_probe_error'` |
| M4: no local timeout | `pre_send_local_timeout_and_late_global_expiry` | `'REFUSED' != 'GO'` |
| M5: publication requires exit | `post_send_hang_is_consumed_once_and_reaped` | `'REFUSED' != 'GO'` |
| M6: empty exit ignored | `exit_without_result_is_error_never_quiet` | `'night_refused_bind_expired' != 'night_probe_error'` |
| M7: cap removed | `oversized_length_and_flood_are_bounded` | `262149 not less than or equal to 262148` |
| M8: partial decode | `slow_chunks_keep_census_and_deadline_fixed` | `'REFUSED' != 'GO'` |
| M9: synchronous journal ACK | `blocked_journal_never_blocks_deadline_or_grants_go` | `external watchdog (8 s)` |
| M10: inherited FD / direct-only kill | `descendant_descriptor_and_group_cancellation` | `False is not true : grandchild inherited result descriptor`; `False is not true : grandchild survived group cancellation` |
| Extra: reset deadline | `QuietBindingTests.test_late_driver_consumes_bind_allowance` | `'night_probe_error' != 'night_refused_bind_expired'` |

Bounded-work arguments, also recorded in code:

- Clocks: fixed comparisons against the deadline computed once.
- Cadence: one nonblocking submission per due tick; at most 32 jobs.
- Launch: anonymous pipe setup and queueing; exec runs on a service thread.
- Transport: four reads and 64 KiB per job/tick; decode at most 256 KiB.
- Results/phases: cached, capped in-memory data; no receive or join.
- Cancellation/reaping: group signals and one `waitpid(WNOHANG)` per job/tick.
- Journal: immutable capped records, nonblocking queue, atomic acknowledgement snapshot; no ticker filesystem I/O.
- Scheduling: timers at most 50 ms; cleanup polls at 1 ms.
- Cost/finalization: two rusage calls and acknowledged digest/count; no journal reread.