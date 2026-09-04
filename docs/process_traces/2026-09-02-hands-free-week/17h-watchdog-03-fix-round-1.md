# Magistrate watchdog — Sol fix round 1

Date: 2026-09-03 PDT  
Base/HEAD at intake: `2b4476cb9a1f81cec4b505b7ac114d217e49301d`  
Branch: `feat/2026-09-03-magistrate-watchdog`  
Install/session/commit actions: none.

## Finding → cure → test

| Finding | Cure | Biting test |
|---|---|---|
| B1 — the real monthly-spend HTTP 429 was `generic_error` | Added case-insensitive signatures for spend limit, `rate_limit`, reset wording without a required preposition, HTTP 429, and retained usage-limit coverage. | `test_real_429_spend_limit_is_usage_exhausted`; `test_usage_classification_is_conservative`; `test_unknown_error_is_generic_error` |
| S1 — a killed Popen child could remain an unreaped zombie and preserve a false lock | `_forced_hold` now calls `child.poll()` inside its one-second loop; PID lookup and tree snapshots exclude `<defunct>` rows. | `test_forced_hold_polls_child_to_reap_defunct_owner`; `test_defunct_lock_owner_is_not_live` |
| S2 — row-4 timing assertions were derived from implementation constants | Pinned literal seconds: plan/request `1500`, TERM `960`, KILL `900`. | `test_plan_fence_boundaries_request_term_kill_and_completion` |
| S3 — row-9 ladder assertion was derived from `USAGE_BACKOFF_S` | Pinned `(900, 1800, 3600, 7200, 7200)` and derived observed jittered values from that literal tuple. | `test_usage_backoff_ladder_and_activation_jitter` |
| S4 — plan enforcement signaled `child.pid` without refreshing authority | TERM and KILL now resolve `owned_process(lock_record, snapshot)` immediately before tree signaling and do not signal if PID/start ownership has vanished. | `test_plan_signal_revalidates_lock_token` |
| N1 — only the cooperative-exit case bit the request-file step | Added an independent request-artifact assertion to the ignored-child TERM/KILL path; the landing report's addendum maps both bites. | `test_cooperative_exit_after_request_never_signals`; `test_ignored_request_gets_term_then_kill_and_census` |
| N2 — stop glob missed shortened emergency names | Widened the ref glob to `refs/heads/ops/stop*` and pinned the `ops/stop-magistrat` case. | `test_stop_glob_catches_shortened_magistrate_branch_name` |
| N3 — fixed-fence orphan-supervisor behavior was implicit | Documented `FENCED`, `adopt=False`, and the at-most-45-minute re-adoption delay (one minute for the 07:00 fence). | Documentation inspection against `decide` fixed-fence ordering |

The clause-map delta is appended, without rewriting the original seat text, under `## Fix round 1 clause-map addendum (2026-09-03 PDT)` in `01-sol-landing-report.md`.

## Focused verification

Command:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog
```

Exit 0 tail:

```text
.................................
----------------------------------------------------------------------
Ran 33 tests in 0.062s

OK
```

Compilation used an external cache so verification created no repository bytecode:

```sh
compile_cache="$(mktemp -d "${TMPDIR:-/tmp}/watchdog-pycompile.XXXXXX")"
PYTHONPYCACHEPREFIX="$compile_cache" python3 -m py_compile scripts/magistrate_watchdog.py
```

Exit 0; no output.

## Mutation probes

Each one-site mutation ran against a fresh restoration of the final watchdog and final focused test module under `/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/watchdog-mutations-final.8lXWZi`; every run exited 1 as expected.

| Mutation | Failing test name(s) |
|---|---|
| `TERM_LEAD_S = 17 * 60` | `test_plan_fence_boundaries_request_term_kill_and_completion` |
| `USAGE_BACKOFF_S[3] = 7199` (source tuple fourth element) | `test_usage_backoff_ladder_and_activation_jitter` |
| Delete the plan `_write_request` step | `test_cooperative_exit_after_request_never_signals`; `test_ignored_request_gets_term_then_kill_and_census` |
| Ignore a failed positive-control result | `test_stop_branch_present_absent_and_positive_control_failure` |
| Flip the belt's closed start boundary to open | `test_fixed_belt_is_half_open` |

## Scope and residual gates

Only the four runner-authorized pathspecs were changed. No LaunchAgent was rendered or installed, no default custody path was used, and no Claude or Codex session was started. This is injected unit/contract evidence, not installed launchd or live-hardware validation; the lead retains the owed bench and final verification gates from the original landing report.
