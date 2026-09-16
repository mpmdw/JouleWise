# 01 — Arm record, `rehearsal-20260916c` (REHEARSAL_STUB), activation `83d93f5a`, 2026-09-16

Re-plan of the lapsed candidate `rehearsal-20260916` (H `cf249594`, t0 03:00;
never published: arm attempt 1 aborted `arm_transport` in activation
`08ca8197`, and `736e2aed` spawned without Gmail tools). Procedure: runbook
§1.3–§1.5 and NIGHT_HANDBACK on main at H, adapted for a stub (no wrapper).
Executed under Ed's directive #349 (tonight clause). **Transport used for the
notice: EMAIL** (Gmail MCP send accepted); the #349 issue fallback was not
needed and was not exercised.

## Frozen checkout triple

| Field | Value |
|---|---|
| `plan_id` | `rehearsal-20260916c` |
| `root` | `/Users/edr/JouleWise-measurement-rehearsal-20260916c` |
| `head` (H) | `be221f6a886498f62154faac0b5da14cb66616a1` (the NIGHT_HANDBACK rewrite commit on main, pushed 02:49 PDT; hosted CI run 35081547655 success) |

## Plan and pins

- Published plan sha256: `aa82ebd961f89cae053fcfb0644b7666b7fb6aec112de7585717a5025c9c1e40` (staged bytes = attempt `plan.json` = published `/Users/edr/night-custody/rehearsal-20260916c/night_plan.json`, `cmp` clean); class `REHEARSAL_STUB`; `window_max_s` 900; `repo_head` = `measurement_head` = H; `custody_root` `/Users/edr/night-custody/rehearsal-20260916c`.
- Clone: `git clone --no-hardlinks` + `checkout --detach` at H (02:49:16–02:49:39); `.venv` Python 3.13.1 from the lock, lock diff EMPTY, mlx 0.31.2 / mlx_lm 0.31.3; canonical ledger restored byte-exact (76 records, custody authentication PASS sequence 76); tree clean.
- Staging: floor from the merged code 600 s; t0 fixed by H; driver preflight ok; `check` / `check --preregistration` informational for a stub (see `01-arm-evidence/30-stage-output.txt`).
- D166 registration sha256 match; `--render-only` rc 0 twice (preflight and arm block).

## Schedule (from `run_night.py schedule`)

| Boundary | Local (PDT, −07:00) | Epoch |
|---|---|---|
| install span 1 (whole day) | 2026-09-16 00:00:00 → 2026-09-17 00:00:00 (excluded) | 1789542000 → 1789628400 |
| install close (excluded) | 2026-09-16 03:15:00 | 1789553700 |
| plan span / exit boundary (REQUEST) | 03:17:00 | 1789553820 |
| TERM / KILL | 03:19:00 / 03:20:00 | 1789553940 / 1789554000 |
| t0 | 03:25:00 | 1789554300 |
| window end / completion (courier deadline) | 03:40:00 / 03:45:00 | 1789555200 / 1789555500 |
| dead-man (daily until uninstalled) | 04:45:00 | 1789559100 |

## Attempt 1 timeline (clock-read)

| Time | Step | Result |
|---|---|---|
| 02:49:44 | preflight arm census (stub rule) | clear: `foreign_pids []`, `workloads []`; own tree + idle interactive `7066` exempt |
| 02:50:06 | NOTICE sent by email (`1a0a99fa2717d749`, thread same) | accepted; `notice.json` + `notice-evidence.txt` written |
| 02:50:26 | pre-arm re-checks | no `standdown.request`/`STOP`; directives unchanged (#349 only, no NO); CI on H success; zero discoverable plans; launchctl = magistrate only |
| 02:50:3x | Gmail read for a NO | none (no owner message newer than 1 day on any thread) |
| 02:50:45 | `40-arm.zsh` | staged checks PASS (1455 s to install close); final census clear; `retry_allowed` allowed; PUBLISHED 1789552244.97; install rc 0; `com.joulewise.night` + `com.joulewise.night.deadman` loaded; calendars match plan; `night/` baseline empty |

Evidence: `01-arm-evidence/` (stage scripts and outputs, attempt files,
census outputs, install output, both plists).

## After the arm

Peer `joulewise-95` informed 02:51. Arm-confirmation reply sent on the notice
thread. This activation exits before 03:17:00 PDT; the night LaunchAgent is the
wake source. Harvest per NIGHT_HANDBACK §Next lane after 03:45:00 PDT and
`courier.sent`; Ed's NO after publication is honoured at the harvest.
