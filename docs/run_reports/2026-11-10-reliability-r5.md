# Reliability round 5 — local Sol seat `rel-r5`

Completed the requested delta leftovers on both local branches. No push,
merge, installation, arm, live hardware check, model download, network access,
or measurement-data read. All hardware behavior remains **PROVISIONAL**.

| Branch | Starting head | Implementation commit |
|---|---|---|
| `ops/2026-11-10-w1-reliability` | `ec0465fd1` | `c6d25d963` |
| `ops/2026-11-10-watchdog-r3` | `origin/ops/2026-11-10-watchdog-unknown-keys` at `343c424e8` | `5e7c60596` |

Branch 2 was created with `git checkout -b` in this clone. No worktree was
created. Returned to branch 1 after committing branch 2; this combined report
is committed on branch 1 separately from its implementation.

## Lead rulings (verbatim)

> - D-02: do NOT restore network time ON on early-refusal paths; record `network_time: left_off` (with reason) instead of `not_owed`/ok. Rationale: the next arm requires it OFF (frequency-word preflight).
> - D-03: launch-abandoned night: dead-man restores power (Automatic) and logs to custody only; never touches night/.
> - D-04: own refusal cause for "a night job is loaded" in prepare (e.g. `prepare.night_job_loaded`); state the ordering (uninstall before prepare) in the runbook text.
> - D-05: copy the phase name and allow-listed refusal codes (e.g. `thermal.start_gate_timeout`) from the driver/r1 result into night/result.json's chain_outcome.
> - D-06: MeterLiveness uses the last non-empty batch.
> - D-01 is NOT yours: leave the registration binding as is (the research lead ratifies it).

> - W-F: gate the exporter flush with `_remote_probe_allowed` (no network git during an armed span); push one pre-span status carrying the span end; the status record says when the next status is expected so the Air poller can hold its staleness alarm.
> - W-H: a missing/failed/old export never blocks a magistrate launch: launch with a `status_export_failed` notice.
> - W-G: latch model-rejection only within a short startup window; otherwise back off.
> - W-I: status host name from `MAGISTRATE_WATCHDOG_STATUS_HOST` (document setting it in the plist).

## Branch 1 dispositions

| Item | Change and synthetic witness |
|---|---|
| D-02 | Early refusals and skipped restores query network time without setting ON. A verified OFF observation records `action: left_off`, the observed state, verification, and the reason that the next arm requires OFF. This subrecord does not claim `ok: true` or `not_owed`. A failed query leaves the overall host close incomplete. The overall close may succeed when power is restored and the deliberate leave-OFF policy is verified. Nights that actually owe an ON restore retain their existing restore path. |
| D-03 | An abandoned launch restores Automatic through the existing ownership/host-lock guards, suppresses network-time ON, and logs only to custody. It creates no night restoration/result/courier record. A pending launcher or unclosed chain defers restoration conservatively; the abandoned path does not resolve or rewrite pending-launch records. The successful witness restores a mode-2 W1 marker and preserves the night directory; the pending-launch witness preserves its file bytes and makes no host calls. |
| D-04 | The frequency preflight reports `prepare.night_job_loaded` for a loaded job and `prepare.night_job_state_unavailable` for an indeterminate census, before any setter/helper call. The magistrate runbook now orders uninstall and authenticated absence before the next prepare. |
| D-05 | `_chain_outcome` copies a refused R1 phase and a sorted fixed vocabulary of code tokens into additive `chain_refused_phase` and `chain_refusal_codes` fields in `night/result.json`. The existing string-valued `chain_outcome` remains compatible. Phase names come from the existing R1 phase table; runtime-kind errors such as `runtime.step-30b` map to `step_30b`. Unknown phases/codes, paths, error prose and numeric suffixes are omitted. The real synthetic terminal-result path proves publication of `thermal.start_gate_timeout` without the injected numeric/private values. |
| D-06 | Empty final polls no longer displace the last non-empty complete batch. That batch's own `rx` still dates it. Empty-only later polls cannot refresh freshness; an invalid final non-empty batch still fails closed. The new witness decodes only the header and selected batch. |
| D-01 | Registration code and receipt template were left unchanged. Research-lead ratification is still owed. |

Copied `/private/tmp/jwsol/briefs/rel-fable-review-delta.md` byte-for-byte over
`docs/run_reports/2026-11-10-w1-reliability-fable-review.md`, including its
Delta review. `cmp` passed; SHA-256:
`5d3dcdfa8ba584212d8d479b6fbe12a1abca01e2e7632d146af2fb1b321b4787`.

Branch-1 files: `scripts/run_night.py`, `scripts/align_v4_session.py`,
`joulewise/b5/driver.py`, `tests/test_w1_reliability_r4.py`,
`tests/test_w1_reliability_r5.py`,
`docs/align/v4/HARVEST-OFF-MAGISTRATE-RUNBOOK.md`, the supplied review copy,
and this combined report.

## Branch 2 dispositions

| Item | Change and synthetic witness |
|---|---|
| W-F | Tick, resident-background and final flushes use the same fresh `_remote_probe_allowed` plan/desk gate. Each Git subprocess rechecks the gate; a 50-second guard before a known span leaves room for the 25-second transport budget. Unknown plan state defers export. Within 410 seconds of the span lead, a changed `span_end_epoch_s` queues a pre-span status. `next_status_expected_epoch_s` is the later of observation time and that end, plus 75 minutes. Air staleness follows that explicit expectation while hold/progress alarms remain active. A real local-bare pre-span push followed by 25 armed ticks, background flush and finish makes zero subsequent publisher calls; delivery resumes after closure. A process-boundary witness proves the gate precedes Popen. |
| W-H | Removed export-dependent launch holds at decision and final launch boundaries. Missing, failed, old and unconfigured exports instead add `status_export_failed` to the launch prompt. The startup path refreshes the notice after version work. Four actual synthetic spawn paths prove the notice is present. Export failure still retains its outbox and lacks an acknowledged delivery receipt. Existing plan/desk fences retain priority. |
| W-G | A model rejection latches only within a 60-second startup window without assistant output. The entire startup stream is inspected so an assistant row outside the diagnostic tail prevents latching. Later model-capacity errors and errors after assistant output use existing backoff. Fast startup rejection remains latched, including before PID observation. No extra model probe or fallback was introduced. |
| W-I | Removed dynamic hostname fallback. Export uses `MAGISTRATE_WATCHDOG_STATUS_HOST`; install and render require a valid stable value before writing. The rendered plist embeds that environment variable. Runtime configuration failure disables export and uses the W-H notice channel. Installer and runtime tests cover missing/invalid names and the pinned plist/ref. |

Branch-2 files: `scripts/magistrate_watchdog.py`, `scripts/watchdog_status.py`,
`scripts/install_magistrate_watchdog.sh`,
`configs/launchd/com.joulewise.magistrate.plist.template`,
`docs/process/MAGISTRATE_WATCHDOG.md`, `tests/test_watchdog_reliability.py`,
and `tests/test_install_magistrate_watchdog.py`.

## Verification

Only targeted unittest modules, serially, under Python 3.13. No full suite.
Commands below use `python3.13 -B -m unittest <target>`. Final targeted runs set
`JW_B5_SYNTHETIC_ONLY=1`; Git-backed runs disabled global/system Git config.
Branch-2 runs also set `GIT_ALLOW_PROTOCOL=file`. Every test remote was a
temporary local bare repository. No real launchd, sudo, meter, model, or agent
activation was used; installer tests use temporary shadow checkouts and stubs.

| Branch | Target | Final result |
|---|---|---|
| 1 | `tests.test_w1_reliability` | 11 passed |
| 1 | `tests.test_w1_reliability_r2` | 18 passed |
| 1 | `tests.test_w1_reliability_r3` | 14 passed |
| 1 | `tests.test_w1_reliability_r4` | 42 passed |
| 1 | `tests.test_w1_reliability_r5` | 7 passed |
| 1 | `tests.align.test_v4_executed_closure` | 4 passed |
| 1 | `tests.align.test_v4_dynamic_closure` | 10 passed |
| 2 | `tests.test_watchdog_reliability` | 39 passed |
| 2 | `tests.test_magistrate_watchdog_v5` | 4 passed |
| 2 | `tests.test_magistrate_watchdog` | 155 passed |
| 2 | `tests.test_install_magistrate_watchdog` | 12 passed |

Baseline round-4 reliability (42) and watchdog reliability (31) also passed
before edits. One intermediate run of the new watchdog spawn witness failed
because it unlinked fixture files before creating the synthetic storage root;
fixed that fixture setup and reran the module successfully. Cumulative reported
unittest runtime, including development reruns, was under three minutes.

`python3.13 -m compileall -q joulewise tests` passed on both branches;
changed watchdog scripts were compiled explicitly too.
`/bin/zsh -n scripts/install_magistrate_watchdog.sh` and `git diff --check`
passed. No native MLX tests were attempted.

Read the speed toolbox from the local `origin/main` Git object. No throughput
claim, batching, decision cache, engine change, measurement threshold/seed
change or measurement-pipeline execution. Ordinary non-empty stream behavior
is preserved; D-06 deliberately changes the reviewed empty-tail case.

## Boundaries, uncertainty and next exact step

Mission M0: inspected the requested status/workspace/restart/stop-card and queue
sections, root AGENTS/CLAUDE, playbook, orchestration and targeted D-050/source
pointers. No active stop card; this explicit reliability brief selected the
AGENT task. Both branches started clean. No delegation or consult.

The brief overrides ordinary coordination writes and the full-suite rule:
`RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json` and
`tests/test_gen_state.py` are unchanged; no task was registered. No external
data path cited in repository text was followed. No real restricted/custody
directory, sealed outcome, model weights or long-running blinded job was read
or operated. Git shared-object access was limited to repository operations.

The native gates in the supplied review remain owed: launchd credentials and
status delivery; Air scheduler/notifier and alarm behavior across a real span;
the CLI's actual model diagnostics; helper/sudo read-backs; USB re-enumeration
and clean-hour restart count; terminal-path power/network policy; and a
launch-abandoned mode-2 case. W-01/W-02 remain **OPEN** until native delivery
and notifications are proven. Tests establish synthetic control flow only.

W-E remains open by design: the watchdog branch was not ported onto the W1
line. The integration lead must port/reconcile it, include `watchdog_status.py`
in the STRICT binding, ratify D-01, refresh closure evidence at the integrated
head and re-register before an arm. The existing committed dynamic trace
already includes the R1 rehearsal module newly consulted by the summary;
this run checked its closure tests and did not regenerate the full trace.
No receipt/signature or registration artifact was minted.

Next exact step: review/cherry-pick `c6d25d963` and `5e7c60596` into the
lead-owned integration lanes, then perform the review's native checks and
STRICT re-registration. No merge or native admission is claimed here.
