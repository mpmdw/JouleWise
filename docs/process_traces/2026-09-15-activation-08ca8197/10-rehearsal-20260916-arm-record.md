# 10 — Arm record, `rehearsal-20260916` (REHEARSAL_STUB), activation `08ca8197`, 2026-09-16

Handoff from the interactive session `b0ae8462` at ~01:55 PDT (installer lane
to this activation; arm the staged stub when main's CI is green and the census
is clean). Procedure: runbook §1.3–§1.5 and NIGHT_HANDBACK on main at H,
adapted for a stub (no wrapper; the driver runs its built-in stub).

## Frozen checkout triple

| Field | Value |
|---|---|
| `plan_id` | `rehearsal-20260916` |
| `root` | `/Users/edr/JouleWise-measurement-rehearsal-20260916b` |
| `head` (H) | `cf249594529cfecf068ca56e6ac8e8d97b78bc77` (the NIGHT_HANDBACK rewrite commit on main) |

## Plan and pins

- Staged plan sha256: `dff929bc09039f72e0edc9f450d357657ec04847bb5b3a872d75b88069d42489`; class `REHEARSAL_STUB`; `window_max_s` 900; `repo_head` = `measurement_head` = H; `custody_root` `/Users/edr/night-custody/rehearsal-20260916`; `chain_path` `<custody_root>/chain.zsh` (never run for a stub); `registration_path` = `night_gate.D166_REGISTRATION_PATH`.
- Clone: `git clone --no-hardlinks` + `checkout --detach` at H; `.venv` Python 3.13.1 from the lock, lock diff EMPTY, mlx 0.31.2 / mlx_lm 0.31.3; canonical ledger restored byte-exact (76 records, custody authentication PASS); tree clean (`03-stage-evidence/20-clone-output-b.txt`, `21-ledger-output-b.txt`).
- Staging (`30-stage-output-b.txt`): floor read from the merged code = 600 s (PLAN_LEAD_S 480 + INSTALL_CLOSE_MARGIN_S 120); t0 fixed by the handback commit; driver preflight ok.
- `check` / `check --preregistration`: rc 3 / rc 3 (the known 25F84→25G83 acceptance-epoch mismatch; informational for a stub).

## Schedule (from `run_night.py schedule`, `35-preflight-output.txt`)

| Boundary | Local (PDT, −07:00) | Epoch |
|---|---|---|
| install span 1 (whole day) | 2026-09-16 00:00:00 → 2026-09-17 00:00:00 (excluded) | 1789542000 → 1789628400 |
| install close (excluded) | 2026-09-16 02:50:00 | 1789552200 |
| plan span / exit boundary (REQUEST) | 02:52:00 | 1789552320 |
| TERM / KILL | 02:54:00 / 02:55:00 | 1789552440 / 1789552500 |
| t0 | 03:00:00 (10:00:00 UTC) | 1789552800 |
| window end | 03:15:00 | 1789553700 |
| completion / courier deadline | 03:20:00 | 1789554000 |
| dead-man (daily) | 04:20:00 | 1789557600 |

`--render-only` from the pinned checkout: rc 0, validated pins repo_head = measurement_head = H, measurement_root as above; both rendered plists in `$STAGE/rendered-agents/`.

## Arm attempt 1 (`$STAGE/arm-attempts/000001/`)

Timeline (PDT): 01:57 handback commit H `cf249594` pushed; 01:59–02:00 clone + ledger; 02:00 staged (`30-stage-output-b.txt`); 02:00:49 preflight (`35-preflight-output.txt`): schedule and boundaries recorded, `--render-only` rc 0, arm census rc 3 on six foreign PIDs = the interactive session's detached bookkeeping seat (pids 93949/94075/94119…, `ppid 1`, outside its session subtree) — a waiting observation, no email; 02:05 census re-run rc 0, CLEAR (`census-0205.txt`: foreign [], workloads [], sessions 841/4493/68602 exempt-idle); 02:11 the interactive session ruled option B (arm on the integration-tree replay at `881a8d6b`, 6240 tests 0 failures + quick tier; hosted CI run `35076281462` on main@`68e5dce6` still QUEUED, recorded as PENDING; the first science night still waits for green CI); 02:11:28 final veto check: directives none, `standdown.request`/STOP absent, watchdog ACTIVE; 02:11–02:12 **Gmail MCP session EXPIRED** on `search_threads` (the NO-relay read) and on `send_message` (the notice). No notice accepted → **no publication, no installer run**; `launchctl list` shows only `com.joulewise.magistrate`; zero discoverable plans; the staged plan remains at `$STAGED_PLAN`.

Attempt 1 outcome (`outcome.json`): cause `arm_transport` (a named mail/API operation failed before publication), `classify_abort` → `retry`, outcome `not_published`, `message_id` empty, `abort_epoch_s` 1789549940. Intended notice preserved verbatim at `/Users/edr/night-custody/magistrate/intended-notice-08ca8197-0212.txt` and here as `notice-body.txt`. The connector is a claude.ai OAuth session; a headless activation cannot re-authorize it, and this activation did not ask the interactive session to send on its behalf (cross-session permission boundary).

Next: attempt 2 = a fresh accepted notice for the same plan bytes if transport returns before ~02:38 (install close 02:50 leaves the notice → publish → install → record sequence its eight minutes), else re-plan t0 under a new handback commit.

## Exit

Not yet: no night is armed, so the activation stays resident (heartbeat, stop-file and directive polls, Gmail re-probe every few minutes).
