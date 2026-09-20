# Activation 3073d213 — launch, night check, hosted-CI finding (2026-09-19 23:28 PDT → exit before 00:32 09-20)

Headless magistrate activation `3073d213-3684-48d5-83f1-91ed1766589d` (watchdog attempt 65),
spawned 23:28:36 PDT 2026-09-19 after activation a743be05 armed pilot night one and exited.
Launch predicates at spawn: remote stop CLEAR, no `standdown.request`, no `STOP`,
`notice_pending` empty. Heartbeat written 23:28:45 (pid 77141). Launch email
`1a0bd8243c302145` to `claude2.glaring610@passmail.net` only; `notice.ack` written.

## The night is armed and untouched (verified read-only at 23:30 PDT)

| Item | Observed |
|---|---|
| Plan | `qpe01-pilot-n1-20260920`, t0 1789890000 = 00:40:00 PDT 09-20 |
| Ladder | REQUEST 00:32, TERM 00:34, KILL 00:35; acquisition end 03:10; courier 03:15; dead-man 04:15 |
| Clone HEAD (`.git/HEAD` read) | `cd10ce9d12f291070a0be77bc8c7768aa5e58ace` = the pinned head |
| LaunchAgents loaded (`launchctl list`) | `com.joulewise.night`, `com.joulewise.night.deadman`, `com.joulewise.magistrate` |
| Plists | `~/Library/LaunchAgents/com.joulewise.night*.plist` written 23:16 |
| Custody root | `chain.zsh` + two digests, `evidence_manifest.json`, `night_plan.json`, `night_probe_receipt.json`, empty `night-probe.{out,err}`, empty `night/` |

No git operation was performed in the canonical root or the measurement clone. Nothing armed,
re-armed, merged, installed or deployed by this activation. No Codex child was started.

## Hosted CI at the code head (the successor's pre-harvest item)

`gh run list --branch main`: `cd10ce9d`, `3bf11df1`, `f04f6972` are docs-only pushes — their runs
are green with `quick`, `test` and both exclusive jobs SKIPPED (8 jobs each). The only full matrix
on the current code is run `35493642148` at the PR #369 merge commit `2f4fc128`:

| Job | Result |
|---|---|
| fences, changes, build, quick, installed-wheel | success |
| calibration-writer-crash-matrix-exclusive ×4 | success |
| calibration-exits-exclusive (3.13) | success |
| calibration-exits-exclusive (3.11) | in progress at 23:33 PDT (past runs: 15–19 min) |
| test (3.13, 1) | success |
| **test (3.11, 3)** | **FAILURE** — step "Unit tests (stdlib core only, per D-009/D-017)" (06:16:30Z → 06:28:48Z) |
| test (3.11, 1/2/4/5/6), test (3.13, 2/3/4/5/6) | cancelled (fail-fast after the shard failure) |

So the Linux matrix at the merged code head is RED on one 3.11 shard and unmeasured on ten
shards. The local full sharded replay at `7ea54846` (record 15 of a743be05, 6,605 tests) and the
modules-alone replay at `0c6626f7` were green on this Mac, so the failure is Linux- or
3.11-specific, or a flake. Job logs are unavailable until the run completes; this activation
waits for completion (background watcher) and appends the failing test below if it arrives
before the exit margin. The mac night does not depend on this run (Ed's 09-16 post-merge rule:
merge on green local replay + quick tier; hosted CI is post-merge confirmation, fix forward).

Failing test(s) at `2f4fc128`, shard `test (3.11, 3)`: see the addendum below (filled by activation cf813934).

## The owed kernel touch is NOT taken here

a743be05 left owed: retire lanes 254 (INSTALLER-RENDER-ONLY-EVIDENCE-01) and 255
(REHEARSAL-MOCK-FREE-01) by removal → 218, unblock 256. A kernel touch is a
`state_kernel.json` edit + `gen_state.py` regeneration + `tests.test_gen_state` live-id update,
historically a seat task (a743be05 record 09 took three attempts). With under an hour to the
ladder's REQUEST it stays owed; the successor takes it at its first kernel touch.

## Addendum (activation cf813934, 23:46 PDT 09-19) — the failing set and its cause

Activation 3073d213 exited at 23:35 before run `35493642148` completed, leaving this record and
its RUN_STATE block uncommitted in its worktree. Activation cf813934 (attempt 66, spawned 23:43:39)
preserved both, read the completed run, and committed them. Run outcome: `completed / failure`;
`calibration-exits-exclusive (3.11)` finished green; only `test (3.11, 3)` is red.

`gh run view --job 106033129389 --log-failed`: `tests.test_install_night_agent` ran 65 tests,
**12 failures, 0 errors** (`FAILED (failures=12)`), every one with the same assertion:

```
AssertionError: 0 != 2 : night wrapper is not valid UTF-8: 'utf-8' codec can't decode byte 0xf0 in position 24: invalid continuation byte
```

Failing tests: `test_dead_man_plist_fires_daily_and_night_plist_once`,
`test_default_python_derivation_with_only_path_python3`, `test_default_python_is_measurement_venv`,
`test_explicit_python_is_the_only_interpreter_in_both_agents`,
`test_explicit_python_overrides_venv_and_preserves_xml_characters`,
`test_install_with_both_pins_matching_renders_both_plists`,
`test_relative_plan_and_render_directory_survive_script_cwd_binding`,
`test_render_only_accepts_staged_stub_and_names_published_plan` (staged=True and staged=False),
`test_render_only_includes_probe_plist_with_pinned_topology`,
`test_rendered_argv0_is_the_validated_python_even_with_token_like_name`,
`test_v3_install_pins_resolved_absolute_plan_in_both_agents`.

Cause (read at the bench, not yet reproduced under Linux): the refusal is raised at
`joulewise/night_agent_install.py:1163` in the PR #369 render-only branch, which reads
`plan.chain_path` as bytes and decodes UTF-8 (an `OSError` keeps the legacy `b""` branch; a
`UnicodeError` refuses — Opus 12 #1 / fresh eyes 17 F1). The legacy render fixture at
`tests/test_install_night_agent.py:103` sets `chain_path="/bin/true"`. On this Mac `/bin/true`
does not exist (`true` lives in `/usr/bin`), so the fixture takes the legacy branch and the module
is green locally (records 15/16b). On the Ubuntu runner `/bin/true` exists and is an ELF64 binary;
byte 24 is the first byte of `e_entry`, here 0xf0, which is not a valid UTF-8 sequence there. So
the failure is a platform-dependent test fixture, not a defect on the armed night's path (the real
plan's `chain.zsh` is UTF-8 text and passed the live render-only step at 23:14).

Fix-forward shape for the successor (Ed's 09-16 rule, twelve-row ledger): point the legacy
fixture at a chain path that is absent on both platforms (or write a real UTF-8 stub), and decide
whether the legacy branch should key on `FileNotFoundError` rather than any `OSError`. Reproduce
under `python3.11` first; the next code PR must show a full green matrix.

No other change was made by cf813934: no git operation in the canonical root or the clone,
nothing under the custody root touched, no Codex child, nothing armed or merged.
